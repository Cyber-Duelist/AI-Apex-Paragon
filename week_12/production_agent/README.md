# Production Agent — Portfolio Project 3

A production-grade autonomous AI agent that analyzes documents, assesses compliance risk, escalates high-risk findings, and notifies stakeholders — all through a FastAPI service with full logging, evaluation, and safety guardrails.

---

## What This Is

This is not a chatbot. It is an autonomous agent that reasons through multi-step compliance tasks, selects the right tools, executes them sequentially, validates its own outputs, and logs every decision. It can be deployed as a REST API and evaluated automatically via CI.

---

## Tech Stack

`Python` · `FastAPI` · `Groq` · `LLaMA 3.3 70B / LLaMA 3.1 8B` · `python-dotenv` · `GitHub Actions`

---

## Project Structure

| File | Purpose |
|---|---|
| `tools.py` | 5 agent tools — search, risk assessment, policy lookup, escalation, notification |
| `memory.py` | Working memory (session) + persistent memory (JSON) |
| `guardrails.py` | Input validation, scope checking, output validation, escalation threshold |
| `agent.py` | Core agent loop — tools, memory, guardrails wired together |
| `main.py` | FastAPI service — `/run`, `/memory`, `/logs`, `/health` endpoints |
| `logs.py` | Structured logger — every tool call, guardrail decision, and response logged |
| `eval.py` | Automated LLM-as-judge evaluation against 4 golden test cases |

---

## Architecture

```
User Request
    ↓
FastAPI /run endpoint
    ↓
Input Guardrails (security + scope check)
    ↓
Query Classifier → routes to Fast Model or Smart Model
    ↓
Agent Loop (ReAct: Reason → Act → Observe)
    ↓
Tools: search_knowledge_base → assess_document_risk → get_compliance_policy
       → create_escalation_ticket → send_notification
    ↓
Output Guardrails (validity check)
    ↓
Logger (every step recorded to agent.log)
    ↓
Structured JSON Response
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Status and active model |
| POST | `/run` | Submit a compliance task to the agent |
| GET | `/memory` | View current session memory and context |
| GET | `/logs` | Last 20 log entries from agent.log |

---

## Example Request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze the Merger Agreement from Legal with 105 pages. Escalate if high risk and notify compliance@company.com"}'
```

```json
{
  "task": "Analyze the Merger Agreement from Legal with 105 pages...",
  "response": "The Merger Agreement has been assessed as high risk. Escalation ticket ESC-538 has been created and compliance@company.com has been notified.",
  "status": "completed",
  "steps_taken": 3,
  "model_used": "llama-3.3-70b-versatile"
}
```

---

## Safety Features

- **Prompt injection detection** — blocks attempts to hijack the agent
- **Scope guardrail** — rejects off-topic tasks before they reach the LLM
- **Output validation** — rejects uncertain or empty responses
- **Escalation threshold** — only escalates if risk score >= 0.7
- **Human-in-the-loop pattern** — established in Week 10, extensible into this agent

---

## Smart Model Routing

Every request is classified as simple or complex before execution:
- Simple tasks → `llama-3.1-8b-instant` — faster, cheaper
- Complex tasks → `llama-3.3-70b-versatile` — more capable

This reduces token usage by up to 4x on routine queries.

---

## Automated Evaluation

```bash
python eval.py
```

Runs 4 test cases scored by LLM-as-judge:
- Standard compliance check
- Multi-step escalation
- Prompt injection resistance
- Out-of-scope rejection

Also runs automatically on every GitHub push via CI pipeline.

---

## How to Run

```bash
# Install dependencies
pip install fastapi uvicorn groq python-dotenv

# Add Groq API key to .env
GROQ_API_KEY=your_key_here

# Start the API
uvicorn week_12.production_agent.main:app --reload

# Run evaluation
python week_12/production_agent/eval.py
```

---

## What I Learned

- A production agent is an LLM plus tools, memory, state, guardrails, logs, and evaluation — removing any one of these makes it a toy, not a system.
- Smart model routing is not just a cost optimization — it is an architectural decision that makes the system more resilient to rate limits and faster on simple tasks.
- Automated evaluation with LLM-as-judge closes the loop — without it you are shipping code you cannot measure.