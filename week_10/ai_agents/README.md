# Week 10: Autonomous AI Agents
A collection of Python-based autonomous AI agents demonstrating tool use, persistent memory, complex planning, and human-in-the-loop safety guardrails.

## What This Covers
This module transitions from linear AI pipelines to cyclical autonomous agents. It explores:
- **Tool Calling:** Teaching LLMs to stop generating text and instead trigger local Python functions.
- **Stateful Memory:** Implementing short-term context windows and long-term global state.
- **Sequential Planning:** Forcing an agent to break down complex goals and execute multi-step operations over datasets.
- **Human-in-the-Loop (HITL):** Building explicit execution pauses for sensitive or irreversible actions.

## Tech Stack
- **Python** (Core Logic & Execution Loop)
- **Groq API** (Ultra-low latency inference)
- **LLaMA 3 Models** (auto-selected via `get_available_model()` — falls back gracefully if a model is retired)
- **python-dotenv** (Environment management)

## Project Structure

| File | Purpose |
|---|---|
| `first_agent.py` | Basic ReAct agent loop capable of understanding context and executing 3 distinct tools. |
| `agent_memory.py` | Demonstrates short-term conversation tracking and long-term dictionary persistence across multiple runs. |
| `planning_agent.py` | Multi-step autonomous planning capable of iterating over multiple documents sequentially. |
| `human_approval.py` | Human-in-the-loop safety guardrail that pauses execution until cryptographic 'yes/no' is received. |

## The Agent Loop Pattern (ReAct)
These agents operate on a continuous `while True:` loop until their goal is achieved:
- **Reason:** The LLM analyzes the prompt, checks its available tool schema, and decides what external data it is missing.
- **Act:** The LLM halts text generation and outputs a structured JSON command, which the Python script catches and uses to execute a local function.
- **Observe:** The Python script injects the function's result back into the LLM's memory array, prompting it to re-evaluate the next step.

## Key Design Decisions
- **Strategic Model Selection:** Dynamically swapping between versatile models for standard tasks and the highly specialized `llama3-groq-70b-8192-tool-use` when strict JSON formatting is required to prevent XML hallucinations during complex planning.
- **Sequential Execution (`parallel_tool_calls=False`):** Forcing the agent to execute one tool at a time ensures data dependency constraints are respected (e.g., getting a risk score *before* attempting to draft a compliance report).
- **Human Gate for Irreversible Actions:** Hardcoding a terminal `input()` pause prior to the `escalate_document` tool guarantees no autonomous agent can execute sensitive operations without human oversight.

## What I Learned
- **Agents are Loops, Not Pipelines:** I shifted my architectural mindset from linear "prompt-to-response" flows to infinite loops that keep the AI alive and thinking until a specific exit condition is mathematically met.
- **Defensive Parsing is Mandatory:** LLMs will occasionally output `null` or malformed JSON when calling zero-parameter tools. Building strict defensive parsing blocks around tool arguments is the only way to prevent runtime crashes.
- **Prompting for Planning:** To get an AI to complete a massive multi-step task, the system prompt must explicitly enforce sequential processing and instruct the model to physically not skip items when iterating over arrays.