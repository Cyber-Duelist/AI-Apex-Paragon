<div align="center">
  <img src="https://cyber-duelist.github.io/AI-Apex-Paragon/og-preview.png" alt="AI Apex Paragon" width="100%" />

  <h1>AI Apex Paragon</h1>
  <p><strong>A 14-week intensive self-directed engineering sprint to build production-ready AI systems from 0 → 1.</strong></p>

  <p>
    <a href="https://cyber-duelist.github.io/AI-Apex-Paragon/"><strong>🌐 View Interactive Portfolio</strong></a> · 
    <a href="https://www.linkedin.com/in/i-am-entity/"><strong>💼 LinkedIn</strong></a> · 
    <a href="mailto:adarshentity098@gmail.com"><strong>✉️ Email</strong></a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/LLaMA_3-0466C8?style=for-the-badge&logo=meta&logoColor=white" alt="LLaMA 3" />
    <img src="https://img.shields.io/badge/ChromaDB-FF4F00?style=for-the-badge&logo=databricks&logoColor=white" alt="ChromaDB" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  </p>
</div>

---

## 🎯 The North Star
**Land a high-paying AI Engineer role by engineering real, deployable, scalable AI systems.** No simple tutorials. No basic API wrappers. Real architectural challenges including Agentic Workflows, Retrieval-Augmented Generation (RAG), and strict LLM Guardrails.

---

## 🏗️ Architecture & Portfolio Projects

### 1. Autonomous Self-Healing DevOps Swarm
A multi-agent orchestration framework that intercepts CI/CD pipeline failures, diagnoses root causes, and writes patches autonomously.
* **Architecture:** Continuous ReAct (Reason + Act) loop routing between `Diagnoser`, `Developer`, `Verifier`, and `PR Reviewer` AI agents.
* **Impact:** Reduces manual debugging time by 90% via zero-touch bug remediation.
* **Tech Stack:** `Python`, `Groq (LLaMA 3)`, `Pytest`, `GitHub API`

### 2. PersonaDoc — Production RAG System
An enterprise-grade document intelligence service that ingests PDFs/TXTs and generates cited, grounded answers.
* **Architecture:** Custom semantic chunking, dense vector retrieval, and output hallucination control.
* **Features:** `/upload`, `/search`, and `/documents` REST endpoints.
* **Tech Stack:** `FastAPI`, `ChromaDB`, `sentence-transformers`, `LLaMA 3.3`

### 3. Enterprise Compliance Agent
A highly secure autonomous agent that analyzes incoming documents, assesses risk, and escalates findings.
* **Architecture:** Stateful memory, strict pre-execution Input Guardrails (against prompt injection), and post-execution Output Guardrails.
* **Reliability:** Dynamic Model Failover routing (e.g., fallback to 8B if 70B hits rate limits) ensuring 99.9% uptime.
* **Tech Stack:** `Python`, `FastAPI`, `GitHub Actions`

### 4. AI Code Reviewer
A microservice that streams raw PR diffs directly from GitHub to a high-reasoning LLM for deep architectural review.
* **Features:** Programmatic JSON schema generation to strictly flag bugs, security vulnerabilities, and logic flaws that standard static analysis tools miss.
* **Tech Stack:** `Python`, `FastAPI`, `GitHub REST API`

### 5. Meeting Intelligence System
A two-stage pipeline that ingests raw meeting transcripts and outputs structured intelligence: summaries, per-person action items with deadlines, and ready-to-send follow-up emails.
* **Tech Stack:** `Python`, `FastAPI`, `Groq`

### 6. Document Risk Prediction (Traditional ML)
A supervised machine learning pipeline classifying documents as high or low risk based on engineered text features.
* **Features:** Feature engineering, hyperparameter tuning, model comparison, and deployment serialization.
* **Tech Stack:** `scikit-learn`, `pandas`, `Random Forest`

---

## 📅 14-Week Curriculum

| Week | Focus Area | Output / Milestone |
|:---:|---|---|
| **1-2** | Python, NumPy, Pandas | Core Foundations |
| **3-4** | ML Fundamentals | Document Risk Prediction Model |
| **5-6** | SQL, FastAPI, Production Python | Database-backed REST API |
| **7** | LLM APIs & Integration | LLM Assistant API |
| **8-9** | RAG Fundamentals + Production | PersonaDoc (RAG System) |
| **10** | Autonomous AI Agents | Multi-Agent Orchestration |
| **11** | LLMOps + Evals | Eval Dashboard, Dynamic LLM Router |
| **12** | Production Agents | Enterprise Compliance Agent |
| **13** | Portfolio Polish | AI Code Reviewer, Meeting Intelligence |
| **14** | **Launch** | Interactive Portfolio & Applications |

---

## 🔮 What's Next?
**ENTITY** — A fully local, voice-controlled AI PC agent using Whisper, local LLaMA models, persistent RAG memory, tool calling, and OS-level automation. *Currently in stealth development.*