# AI Apex Paragon

A 14-week intensive self-directed program to become a production-ready AI Engineer — from Python foundations to RAG systems, autonomous agents, and LLMOps.

---

## Goal

Land a high-paying AI Engineer / GenAI Engineer role by building real, deployable AI systems — not tutorials, not clones.

---

## Portfolio Projects

### 1. PersonaDoc — Production RAG System
Upload any PDF or TXT. Ask questions. Get cited answers grounded in the document.
- ChromaDB vector store, reranking, hallucination control, eval pipeline
- FastAPI service with `/upload`, `/search`, `/documents` endpoints
- **Tech:** Python, FastAPI, ChromaDB, sentence-transformers, Groq, LLaMA 3.3

### 2. Production Compliance Agent — Agentic Workflow
Autonomous agent that analyzes documents, assesses risk, escalates findings, and notifies stakeholders.
- Tools, memory, guardrails, structured logging, LLM-as-judge eval
- Smart model routing — fast model for simple tasks, powerful model for complex ones
- CI pipeline runs automated evaluation on every push
- **Tech:** Python, FastAPI, Groq, LLaMA 3.3, GitHub Actions

### 3. AI Code Reviewer
Submit any GitHub PR URL. Get a structured LLM-powered code review with bugs, security issues, severity ratings, and approval decision.
- Connects to real GitHub API — fetches actual diffs, not sample code
- **Tech:** Python, FastAPI, Groq, GitHub API

### 4. Meeting Intelligence System
Upload any meeting transcript. Get structured intelligence — summary, per-person action items with deadlines, decisions made, and a ready-to-send follow-up email.
- Two-stage LLM pipeline — analyze then draft
- **Tech:** Python, FastAPI, Groq, LLaMA 3.3

### 5. Autonomous Self-Healing DevOps Swarm
A multi-agent orchestration system that automatically intercepts CI/CD pipeline failures, diagnoses the root cause, writes a patch, verifies the fix, and opens a GitHub Pull Request.
- Continuous "ReAct" Loop routing between Diagnoser, Developer, Verifier, and PR LLM Agents.
- **Tech:** Python, Groq, Pytest, Multi-Agent Orchestration

### 6. LLMOps Evaluation Dashboard
A real-time evaluation dashboard to test LLM agents against strict compliance and security datasets.
- Implements automatic Model Failover (routing to 8B if 70B hits rate limits) ensuring 99.9% uptime.
- **Tech:** Python, FastAPI (SSE Streaming), JavaScript, HTML/CSS

### 7. Document Risk Prediction — ML Project
Classify documents as high or low risk using machine learning.
- Feature engineering, model comparison, hyperparameter tuning, saved prediction pipeline
- **Tech:** Python, scikit-learn, pandas, Random Forest

---

## Tech Stack

`Python` · `FastAPI` · `Groq` · `LLaMA 3.3` · `ChromaDB` · `sentence-transformers` · `scikit-learn` · `Docker` · `pytest` · `GitHub Actions` · `SQLite` · `Pydantic`

---

## Curriculum — 14 Weeks

| Week | Focus | Output |
|---|---|---|
| 1-2 | Python, NumPy, Pandas | Foundations |
| 3-4 | ML Fundamentals | Document Risk Prediction |
| 5-6 | SQL, FastAPI, Production Python | Database-backed API |
| 7 | LLM APIs | LLM Assistant API |
| 8-9 | RAG Fundamentals + Production | PersonaDoc |
| 10 | AI Agents | Agent patterns |
| 11 | LLMOps + Evals | Eval dashboard, LLM router |
| 12 | Production Agent | Compliance Agent |
| 13 | Portfolio Polish + Extra Projects | AI Code Reviewer, Meeting Intelligence |
| 14 | Job Attack | Applications and interviews |

---

## North Star

**ENTITY** — a fully local, voice-controlled AI PC agent using Whisper, LLaMA via Ollama, RAG memory, tool calling, and OS automation. Built in private. Coming soon.