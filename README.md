# Autocommit

Automatic commit message generation tool powered by AI. Will support multiple AI models (GPT, DeepSeek, Gemini, Llama, etc.)

This project's commit messages will almost always be generated from this tool.

---

## Setup

1. For now, this project only supports DeepSeek API (DeepSeek's API pricing is significantly lower than that of ChatGPT's, and DeepSeek is very much feasible for a simple task like generating a commit message, which might require large inputs for large changes. Get an api from the [Deepseek Platform](https://api-docs.deepseek.com/zh-cn/api/deepseek-api/))
2. Add your API key to the .env file:
```env
DEEPSEEK_API_KEY=<your-api-key>
```
3. Install pyinstaller and other dependencies via pip:
```bash
pip install pyinstaller requests dotenv
```
4. 'Compile' python file to binaries via this command:
```bash
pyinstaller --onefile main.py
```
5. Add output directory (```dist/```) to Path
6. Set up context for your project:
```bash
autocommit --context <your-project-context>
```
7. Make changes and add to Git. If you didn't add anything to the stage yet there are changes in your project, autocommit prompts you to add files:
```bash
git add . # or your specific files to add to stage.
```
8. Autocommit and verify commit message. If you don't like it, you can change the file named `.autocommit` which stores project context, or you can manually create a commit message.
```bash
autocommit
```
