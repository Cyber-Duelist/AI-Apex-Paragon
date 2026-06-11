# Meeting Intelligence System

A FastAPI service that analyzes meeting transcripts and returns structured intelligence — summary, action items per person, decisions made, and a ready-to-send follow-up email.

---

## What This Does

Paste any meeting transcript and get back a complete structured analysis. The system identifies every participant, extracts decisions made, assigns action items with deadlines per person, and drafts a professional follow-up email — all in one API call.

---

## Tech Stack

`Python` · `FastAPI` · `Groq` · `LLaMA 3.3 70B` · `python-dotenv`

---

## Project Structure

| File | Purpose |
|---|---|
| `analyzer.py` | Extract summary, action items, decisions, participants from transcript |
| `email_drafter.py` | Draft professional follow-up email from meeting analysis |
| `main.py` | FastAPI service — POST /analyze endpoint |

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Status and active model |
| POST | `/analyze` | Submit transcript, get structured analysis and email |

---

## Example Request

```json
{
  "transcript": "John: Let's start the sprint planning...",
  "include_email": true
}
```

---

## Example Response

```json
{
  "summary": "Sprint planning meeting where tasks were assigned...",
  "participants": ["John", "Sarah", "Mike", "Tom"],
  "meeting_type": "planning",
  "decisions": ["Use PostgreSQL instead of MySQL", "Move standup to 9am"],
  "action_items": [
    {"person": "Sarah", "task": "user authentication feature", "deadline": "Friday"},
    {"person": "Mike", "task": "database migration", "deadline": "Wednesday"}
  ],
  "email_subject": "Sprint Planning Meeting Follow-up and Action Items",
  "email_body": "Dear Team..."
}
```

---

## How to Run

```bash
pip install fastapi uvicorn groq python-dotenv
uvicorn week_13.meeting_intelligence.main:app --reload
```

Add your Groq API key to `.env` at project root:

## What Makes This Different

This is not a summarizer. It extracts structured, actionable intelligence — who owns what, by when, and what was decided. The follow-up email is generated automatically from the extracted data, not from the raw transcript, making it accurate and consistent every time.

---

## What I Learned

- Structured JSON outputs from LLMs are only reliable when the system prompt is extremely explicit about key names and value types — ambiguity leads to inconsistent schemas.
- Chaining two LLM calls (analyze then draft email) produces better results than one large prompt — each model call has a focused, well-defined job.
- Caching the model selection at module load time prevents unnecessary API calls and significantly reduces token consumption across multiple requests