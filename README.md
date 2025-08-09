# Autocommit

#### !! This is not a spam tool for boosting your github activity !!

This is an automatic commit message generation tool powered by AI. Will support multiple AI models (GPT, DeepSeek, Gemini, Llama, etc.)

This project's commit messages will almost always be generated from this tool.

This tool works by looking at ```git diff```'s, analyzing the differences, tying them with context, and generating a commit message. For better context enrichment for the commit generator, consider adding more comments to your code.

---

## Setup
First, clone the repository: 
```bash
git clone https://github.com/Eddy12597/Autocommit.git
cd Autocommit
```
1. For now, this project only supports DeepSeek API (DeepSeek's API pricing is significantly lower than that of ChatGPT's, and DeepSeek is very much feasible for a simple task like generating a commit message, which might require large inputs for large changes. Get an api from the [Deepseek Platform](https://api-docs.deepseek.com/zh-cn/api/deepseek-api/))
2. Add your API key to the .env file:
```env
DEEPSEEK_API_KEY=<your-api-key>
```
3. Install pyinstaller and other dependencies via pip:
```bash
pip install pyinstaller requests dotenv
```
4. 'Compile' the ```.spec``` file to binaries via this command. This may take around 40~80 seconds:
```bash
pyinstaller autocommit.spec
```
If errors occur (e.g. "ERROR: Aborting build process due to attempt to collect multiple ___ bindings packages: ..."), modify the ```autocommit.spec``` file to exclude problematic libraries:
```python
a = Analysis (
	# ... other parameters
	excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6'], # add more if needed
	# ... rest of the parameters
)
```
5. Add output directory (```/path/to/Autocommit/dist/```) to Path
6. Set up context for your project:
```bash
autocommit --context <your-project-context>
```
7. Make changes and add to Git. If you didn't add anything to the stage yet there are changes in your project, autocommit prompts you to add files:
```bash
git add . # or your specific files to add to stage.
```
8. Autocommit and verify commit message. If you don't like it, you can change the file named `.autocommit` which stores project context, or you can manually create a commit message. This takes about 5~10 seconds. Add the ```--push``` flag to let it prompt you to push to remote (this saves 2 characters of typing lol)
```bash
autocommit
```

---
Todo/Future:
1. Enhance error/exception management for clearer error messages
2. Rewrite in a compiled language to save compilation time