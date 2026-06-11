import os
import json
from dotenv import load_dotenv
from analyzer import analyze_transcript, _client, _model, SAMPLE_TRANSCRIPT

load_dotenv()

def draft_followup_email(analysis: dict) -> dict:
    """Draft a professional follow-up email from meeting analysis."""

    system_prompt = """You are a professional meeting secretary.
Based on the meeting analysis provided, write a follow-up email.
Return ONLY valid JSON with two keys:
- subject: email subject line
- body: full professional email body with summary, decisions, and action items"""

    user_prompt = f"""Meeting Analysis:
Summary: {analysis.get('summary')}
Participants: {analysis.get('participants')}
Meeting Type: {analysis.get('meeting_type')}
Decisions: {analysis.get('decisions')}
Action Items: {analysis.get('action_items')}"""

    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    print("=== ANALYZING TRANSCRIPT ===")
    analysis = analyze_transcript(SAMPLE_TRANSCRIPT)
    print("Analysis complete.\n")

    print("=== DRAFTING FOLLOW-UP EMAIL ===")
    email = draft_followup_email(analysis)

    print(f"Subject: {email.get('subject')}\n")
    print(f"Body:\n{email.get('body')}")