# Week 10: Autonomous AI Agents

A collection of Python-based autonomous AI agents demonstrating tool use, persistent memory, complex planning, and human-in-the-loop safety guardrails. 

This week features a complete **Cyberpunk Agent Visualizer Web Dashboard** built with FastAPI, allowing you to watch the agent "think", parse uploaded files, and ask for permission before executing dangerous tools!

## What This Covers
This module transitions from linear AI pipelines to cyclical autonomous agents. It explores:
- **Tool Calling:** Teaching LLMs to stop generating text and instead trigger local Python functions.
- **Stateful Memory:** Implementing short-term context windows and long-term global state.
- **Human-in-the-Loop (HITL):** A stateless architecture where the AI pauses execution and pings the UI for explicit human approval before doing something dangerous.
- **Live Document Parsing:** Autonomous text extraction from uploaded `.pdf`, `.txt`, `.csv`, and `.md` files directly into the agent's context.

## Tech Stack
- **Python (FastAPI)** (Backend execution loop)
- **Vanilla JS + CSS** (Frontend visualizer)
- **Groq API** (Ultra-low latency inference for live agent thinking)
- **PyPDF2** (For extracting raw text from uploaded files)

## Project Structure

| File | Purpose |
|---|---|
| `main.py` | FastAPI backend serving the Web UI and handling the Server-Sent Events (SSE) agent streams. |
| `first_agent.py` | The core agent engine with dynamic tool execution, memory cleanup, and failover model logic. |
| `static/app.js` | Frontend logic for handling continuous chat memory, Markdown parsing, and HITL approvals. |
| `agent_memory.py` | CLI demo for short-term conversation tracking. |
| `planning_agent.py` | CLI demo for multi-step autonomous planning capable of iterating over multiple documents. |

## The Agent Loop Pattern (ReAct)
These agents operate on a continuous loop until their goal is achieved:
- **Reason:** The LLM analyzes the prompt, checks its available tool schema, and decides what external data it is missing.
- **Act:** The LLM halts text generation and outputs a structured JSON command, which the Python script catches and uses to execute a local function.
- **Observe:** The Python script injects the function's result back into the LLM's memory array, prompting it to re-evaluate the next step.

## Key Design Decisions
- **Stateless Server-Sent Events:** Using SSE allows us to stream the agent's thought process live to the browser without web sockets.
- **Stateless HITL Pausing:** If the agent requests a dangerous tool (`save_file` or `escalate_document`), the server stops the loop and returns memory to the frontend. This saves server resources while waiting for the human to click Approve/Reject.
- **Silent Model Failover:** Built a system to gracefully and silently failover from the 70B Versatile model to the 8B Instant model in the event of API rate limits, ensuring the user experience remains uninterrupted and without alarming error messages.

## What I Learned
- **Agents are Loops, Not Pipelines:** I shifted my architectural mindset from linear "prompt-to-response" flows to infinite loops that keep the AI alive and thinking until a specific exit condition is mathematically met.
- **Payload Sanitization is Critical:** LLM APIs are extremely strict about the JSON schemas of `messages`. I had to build a cleanup layer to strip out unneeded SDK metadata before passing memory history back to the API.
- **Human Gate for Irreversible Actions:** Building the HITL architecture over a stateless HTTP protocol requires clever memory injection, essentially injecting a fake `tool` observation to tell the LLM that the human rejected its request!

For instructions on how to run and use the dashboard, see the [USER_MANUAL.md](./USER_MANUAL.md).