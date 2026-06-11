import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from analyzer import analyze_transcript, _model
from email_drafter import draft_followup_email

app = FastAPI(title="Meeting Intelligence API")

# Pydantic Models
class TranscriptRequest(BaseModel):
    transcript: str
    include_email: bool = True

class MeetingResponse(BaseModel):
    summary: str
    participants: list
    meeting_type: str
    decisions: list
    action_items: list
    email_subject: str
    email_body: str


# Endpoints
@app.get("/")
def root():
    return {"status": "Meeting Intelligence API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "model": _model}

@app.post("/analyze", response_model=MeetingResponse)
def analyze(req: TranscriptRequest):
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    # Analyze transcript
    analysis = analyze_transcript(req.transcript)

    # Draft email if requested
    email_subject = ""
    email_body = ""
    if req.include_email:
        email = draft_followup_email(analysis)
        email_subject = email.get("subject", "")
        email_body = email.get("body", "")

    return MeetingResponse(
        summary=analysis.get("summary", ""),
        participants=analysis.get("participants", []),
        meeting_type=analysis.get("meeting_type", "general"),
        decisions=analysis.get("decisions", []),
        action_items=analysis.get("action_items", []),
        email_subject=email_subject,
        email_body=email_body
    )