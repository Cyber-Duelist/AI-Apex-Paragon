# Week 14: Autonomous Self-Healing DevOps Swarm

A multi-agent orchestration system that automatically intercepts CI/CD pipeline failures, diagnoses the root cause, writes a patch, verifies the fix with local testing, and opens a GitHub Pull Request.

---

## 🚀 What This Does

Standard CI/CD pipelines fail and wait for a human engineer to read the logs, write a fix, and push a new branch. This project introduces **Active AI Agents**. 

When the `webhook_simulator.py` detects a test failure, it triggers a "ReAct" Swarm Loop:
1. **Diagnoser Agent**: Reads the raw pytest failure logs and isolates the bug.
2. **Developer Agent**: Uses custom tools to read the source code, write a patch, and overwrite the file.
3. **Verifier Agent**: Runs the test suite in a local sandbox to prove the code works. (If it fails, it sends the new logs back to the Developer in a continuous loop).
4. **PR Agent**: Drafts a professional Pull Request summary detailing the fix.

---

## 🛠️ Tech Stack

`Python` · `Groq API` · `LLaMA 3.1 8B` · `Pytest` · `Multi-Agent Orchestration`

---

## 📂 Project Structure

| File | Purpose |
|---|---|
| `orchestrator.py` | The main Swarm Loop that manages context passing between agents. |
| `agents.py` | Defines the LLM personas (Diagnoser, Developer, Verifier, PR Agent). |
| `tools.py` | File I/O and shell execution tools for the AI to interact with the OS. |
| `webhook_simulator.py` | Triggers a mock CI/CD pipeline failure to start the Swarm. |
| `mock_repo/` | A sandboxed Python repository with intentional bugs for the AI to fix. |

---

## ⚙️ How to Run

1. Ensure your `.env` file at the root of the project contains your `GROQ_API_KEY`.
2. Activate your virtual environment.
3. Intentionally break the code in `mock_repo/calculator.py` (e.g., change `return a + b` to `return a - b`).
4. Run the simulator to trigger the Swarm:

```bash
# On Windows PowerShell, ensure UTF-8 encoding is active
$env:PYTHONIOENCODING="utf-8"
python webhook_simulator.py
```

Watch the terminal as the agents collaborate to read your code, patch your bug, run the tests, and output a PR!
