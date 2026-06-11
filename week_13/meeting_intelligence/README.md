# Meeting Intelligence System

A production-grade B2B SaaS application that analyzes meeting transcripts and returns structured intelligence — summary, action items per person, decisions made, and a ready-to-send follow-up email.

---

## What This Does

Paste any meeting transcript into the **Luxury Dashboard** and get back a complete structured analysis. The system identifies every participant, extracts decisions made, assigns action items with deadlines per person, and drafts a professional follow-up email — all in one click.

---

## Tech Stack

`Python` · `FastAPI` · `Groq` · `Vanilla JS/CSS (Glassmorphism & Dark Mode)`

---

## Project Structure

| File | Purpose |
|---|---|
| `analyzer.py` | Extract summary, action items, decisions, participants from transcript |
| `email_drafter.py` | Draft professional follow-up email from meeting analysis |
| `main.py` | FastAPI service — backend endpoints and Static File Server |
| `static/index.html` | Premium Two-Column Dashboard UI |
| `static/style.css` | Luxury Corporate Theme (Light/Dark Mode, Glassmorphism) |
| `static/app.js` | API connection, JSON parsing, and UI rendering logic |

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Serves the frontend web dashboard |
| GET | `/health` | Status and active model |
| POST | `/analyze` | Submit transcript, get structured analysis and email |

---

## How to Run

```bash
pip install fastapi uvicorn groq python-dotenv

# Start the API and Dashboard
uvicorn main:app --port 8000
```

Add your Groq API key to `.env` at project root:
`GROQ_API_KEY=your_key_here`

Open your browser and navigate to:
**http://localhost:8000**

---

## What Makes This Different

This is not a simple summarizer. It extracts **structured, actionable intelligence** — who owns what, by when, and what was decided. The follow-up email is generated automatically from the extracted data, not from the raw transcript, making it accurate and consistent every time. 

The frontend uses an ultra-premium CSS design system with micro-interactions, floating cards, and a flawless Dark Mode.

---

## What I Learned

- Structured JSON outputs from LLMs are only reliable when the system prompt is extremely explicit about key names and value types — ambiguity leads to inconsistent schemas. We handled this by making our JavaScript resilient to alternative keys (e.g. `due_date` vs `deadline`).
- Chaining two LLM calls (analyze then draft email) produces better results than one large prompt — each model call has a focused, well-defined job.
- Caching the model selection at module load time prevents unnecessary API calls and significantly reduces token consumption across multiple requests.