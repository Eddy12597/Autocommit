import os
import subprocess
import argparse
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ["PYTHONUTF8"] = "1"  # Force UTF-8 encoding

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
CONTEXT_FILE = ".autocommit"
README_FILE = "README.md"
GITIGNORE = ".gitignore"

def get_project_context():
    """Get project context from .autocommit and README.md if they exist."""
    context_parts = []
    
    # Check .autocommit file
    if Path(CONTEXT_FILE).exists():
        if Path(GITIGNORE).exists():
            with open(GITIGNORE, "r") as f:
                if CONTEXT_FILE not in f.read():
                    print(f"⚠️  Add '{CONTEXT_FILE}' to {GITIGNORE} to avoid committing it.")
        
        with open(CONTEXT_FILE, "r") as f:
            context_parts.append(f.read().strip())
    
    # Check README.md file
    if Path(README_FILE).exists():
        with open(README_FILE, "r") as f:
            readme_content = f.read().strip()
            if readme_content:  # Only add if not empty
                context_parts.append(f"README.md content:\n{readme_content}")
    
    if not context_parts:
        print(f"⚠️  No project context found. Add context with:")
        print(f"   autocommit --context \"Your project description...\"")
        return None
    
    return "\n\n".join(context_parts)

def save_context(context):
    """Save --context to .autocommit."""
    with open(CONTEXT_FILE, "w") as f:
        f.write(context)
    print(f"✅ Saved context to {CONTEXT_FILE}")

def get_git_diff():
    """Get diff, excluding binaries."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--no-color", "--", ":!*.png", ":!*.jpg", ":!*.pdf"],
            capture_output=True,
            text=True,
            encoding='utf-8',  # Explicit encoding
            errors='replace'  # Replace undecodable characters
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to get git diff: {e}")
        return ""  # Return empty string instead of None

def generate_commit_message(diff, context=None):
    """Call DeepSeek with project context."""
    system_prompt = (
            "Generate a concise Git commit message using conventional commits (fix:, feat:, doc:, etc.). "
        f"Project context: {context}\n\nChanges:"
    )
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": diff}
        ]
    }
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json=payload
        )
        return response.json()["choices"][0]["message"]["content"].strip('"\' \n')
    except Exception as e:
        print(f"❌ API error: {e}")
        print("Consider checking if API key i correct")
        print(f"API Response: {response}")
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", help="Set project context (saved to .autocommit)")
    parser.add_argument("--push", action="store_true", help="Push after commit (with confirmation)")
    args = parser.parse_args()

    if args.context:
        save_context(args.context)
        return

    context = get_project_context()
    if context is None:
        exit(1)

    diff = get_git_diff()
    if not diff:
        # Check for unstaged changes
        unstaged = subprocess.run(["git", "diff", "--no-color"], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.strip()
        if unstaged:
            print("❌ No staged changes detected, but there are unstaged changes.")
            if input("Stage all changes with 'git add .'? [Y/n]: ").lower() in ("", "y", "yes"):
                subprocess.run(["git", "add", "."], check=True)
                diff = get_git_diff()
                if not diff:
                    print("❌ Still no staged changes. Exiting.")
                    exit(1)
            else:
                print("❌ No changes staged. Exiting.")
                exit(1)
        else:
            print("❌ No text changes detected. Stage changes with 'git add'.")
            exit(1)

    message = generate_commit_message(diff, context)
    print(f"\n📝 Suggested commit:\n\t{message}\n")
    if input("Commit? [Y/n]: ").lower() in ("", "y", "yes"):
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("✅ Commit done!")
        if args.push:
            if input("Push to remote? [Y/n]: ").lower() in ("", "y", "yes"):
                subprocess.run(["git", "push"], check=True)
                print("🚀 Pushed!")

if __name__ == "__main__":
    main()
