# Week 11: LLMOps & Evaluation
An enterprise-grade LLMOps pipeline featuring prompt versioning, automated evaluation, telemetry tracing, and intelligent model routing.

## What This Covers
This module transitions from building AI features to operating AI systems in production. It covers LLMOps fundamentals:
- **Prompt Versioning:** Treating prompts as immutable code to track changes over time.
- **LLM-as-a-Judge Evaluation:** Using high-reasoning models to mathematically score outputs against strict rubrics.
- **Tracing & Telemetry:** Passively tracking latency, token consumption, and cost per API call.
- **Eval Dashboards:** Running CI/CD-style test suites against a Golden Dataset.
- **Intelligent Model Routing:** Dynamically classifying user queries to route them to the most cost-effective and performant model.

## Tech Stack
- **Python** (Core Logic)
- **Groq API** (Ultra-low latency inference)
- **LLaMA 3.3 70B** (The "Smart" Model / Judge)
- **LLaMA 3.1 8B** (The "Fast" Model / Router)
- **python-dotenv** (Environment management)

## Project Structure

| File | Purpose |
|---|---|
| `prompt_versioning.py` | Version and diff prompts across iterations using a central registry. |
| `llm_judge.py` | Score LLM responses using a second high-capability LLM as an impartial judge. |
| `tracer.py` | A custom decorator to track latency, tokens, and cost per LLM call. |
| `eval_dashboard.py` | Golden dataset eval pipeline outputting pass/fail metrics and telemetry. |
| `llm_router.py` | Triage agent to route queries to a fast or smart model based on complexity. |
| `traces.json` | Persisted trace logs from tracer runs (observability data). |

## Key Results
- **Eval Dashboard:** Achieved an **80% pass rate**, avg score **4.2/5**, and a total cost of **$0.000614** across the Golden Dataset.
- **Router Efficiency:** Correctly classified 100% of the 5 test queries. Simple queries routed to the 8B model used **4-15x fewer tokens** and returned in a fraction of the time.

## What I Learned
- **Vibes vs. Metrics:** You cannot improve what you cannot measure. Automated evaluation pipelines allow me to mathematically prove whether a prompt tweak actually improved the system.
- **Observability via Decorators:** Building a `@trace` wrapper is the cleanest way to capture latency, token usage, and fractional-cent costs without cluttering the core application logic.
- **Semantic Routing is Crucial:** Routing every request to a massive 70B model is a massive waste of compute. An 8B triage router drastically reduces costs and latency for basic queries while reserving heavy compute for deep reasoning tasks.