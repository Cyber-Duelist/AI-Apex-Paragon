# Autonomous Agent Visualizer - User Manual

Welcome to the Week 10 Autonomous Agent Visualizer. This dashboard allows you to interact with a general-purpose ReAct AI Desktop Assistant, watch its internal thought process, upload real documents for it to analyze, and safely approve its sensitive actions.

## 1. Getting Started

1. **Start the Server:** Ensure your virtual environment is active, then run:
   ```bash
   python -m uvicorn main:app --port 8000
   ```
2. **Access the Dashboard:** Open your web browser and navigate to `http://localhost:8000`.

## 2. Basic Prompting

The AI is equipped with tools to help you manage your digital life and do research.
- In the text box at the bottom, type: *"Search the web for the latest updates on Python 3.12 and give me a summary."*
- Click **EXECUTE**. 
- You will see the agent call the `search_web` tool, pull data from Wikipedia, and output a beautifully formatted Markdown response.

## 3. Uploading and Parsing Documents

The agent can autonomously read documents you upload to the dashboard. Supported formats: `.pdf`, `.txt`, `.md`, `.csv`.

1. Click the **Upload Button** (the square with an arrow pointing up) inside the prompt input bar.
2. Select a document from your computer. 
3. Wait for the green success message indicating the file was saved.
4. Your prompt bar will automatically pre-fill with a suggestion to read the file. Click **EXECUTE**.
5. The agent will trigger its `read_uploaded_document` tool to read the file locally and summarize its contents.

## 4. Local Desktop Integration

The agent can see files on your computer and generate files for you!
- **List Files:** Try prompting *"List the files in my current directory."* The agent will use `list_local_files` to show you what's there.
- **Write Code:** Try prompting *"Write a Python script that calculates the Fibonacci sequence and save it to 'fibonacci.py'."* The agent will generate the code and trigger the `save_file` tool!

## 5. Testing Human-in-the-Loop (HITL) Guardrails

Because giving an AI the power to write files to your hard drive is dangerous, we have designated `save_file` as a **Dangerous Action**.

1. When the agent attempts to save a file (like in the Fibonacci example above), **the dashboard will flash red.** Execution has been paused.
2. **Click APPROVE:** The dashboard will execute the Python script, actually save the file to your computer, and the AI will finalize its output.
3. **Click REJECT:** The dashboard will inject a rejection notice into the AI's memory. The AI will wake back up and apologize to you for failing the task!

## 6. Continuous Memory

The dashboard tracks your conversation history. If you uploaded a document or searched the web in a previous prompt, you can type a follow-up question:
- *"Wait, what was the third point mentioned in that article?"*
The agent will rely on its memory (and past tool observations) to answer you immediately without re-running the tools!
