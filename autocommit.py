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
GITIGNORE = ".gitignore"

def check_context_file():
    """Ensure .autocommit exists and is gitignored."""
    if not Path(CONTEXT_FILE).exists():
        print(f"⚠️  {CONTEXT_FILE} not found. Add project context with:")
        print(f"   autocommit --context \"Your project description...\"")
        return None
    
    if Path(GITIGNORE).exists():
        with open(GITIGNORE, "r") as f:
            if CONTEXT_FILE not in f.read():
                print(f"⚠️  Add '{CONTEXT_FILE}' to {GITIGNORE} to avoid committing it.")
    
    with open(CONTEXT_FILE, "r") as f:
        return f.read().strip()

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
        "Generate a concise Git commit message using conventional commits (fix:, feat:, etc.). "
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
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", help="Set project context (saved to .autocommit)")
    args = parser.parse_args()

    if args.context:
        save_context(args.context)
        return

    context = check_context_file()
    if context is None:
        exit(1)

    diff = get_git_diff()
    if not diff:
        print("❌ No text changes detected. Stage changes with 'git add'.")
        exit(1)

    message = generate_commit_message(diff, context)
    print(f"\n📝 Suggested commit:\n\t{message}\n")
    if input("Commit? [Y/n]: ").lower() in ("", "y", "yes"):
        subprocess.run(["git", "commit", "-m", message], check=True)
        print("✅ Done!")

if __name__ == "__main__":
    main()
