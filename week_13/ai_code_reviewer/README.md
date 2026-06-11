# AI Code Reviewer

A FastAPI service that accepts any GitHub Pull Request URL, fetches the real code diff, and returns a structured LLM-powered code review with bugs, security issues, suggestions, and severity ratings.

---

## What This Does

AI Code Reviewer connects directly to the GitHub API to fetch real PR diffs — not sample code, not hardcoded examples. It sends the actual changed code to an LLM and returns a structured JSON review that engineering teams can act on immediately.

---

## Tech Stack

`Python` · `FastAPI` · `Groq` · `LLaMA 3.3 70B` · `GitHub API` · `python-dotenv`

---

## Project Structure

| File | Purpose |
|---|---|
| `github_client.py` | Parse PR URLs, fetch PR metadata and raw diffs from GitHub API |
| `reviewer.py` | Send diff to LLM, return structured JSON review |
| `main.py` | FastAPI service with /review endpoint |

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Status and active model |
| POST | `/review` | Submit a GitHub PR URL and get a structured code review |

---

## Example

Request:
```json
{
  "pr_url": "https://github.com/pallets/flask/pull/5446"
}
```

Response:
```json
{
  "pr_url": "https://github.com/pallets/flask/pull/5446",
  "title": "fix broken HTML markup",
  "author": "DanielSiepmann",
  "summary": "This PR fixes broken HTML markup in a template inheritance documentation file by adding a closing paragraph tag",
  "bugs": [],
  "security_issues": [],
  "suggestions": ["Consider adding automated tests to catch similar markup issues in the future"],
  "severity": "low",
  "approved": true
}
```

---

## How to Run

```bash
pip install fastapi uvicorn groq python-dotenv requests
uvicorn week_13.ai_code_reviewer.main:app --reload
```

Add your Groq API key to `.env` at project root: