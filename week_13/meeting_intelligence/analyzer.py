import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_available_model():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
    for model in preferred_models:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            print(f"Using model: {model}")
            return model
        except Exception:
            continue
    raise Exception("No available models found.")

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_model = get_available_model()

def analyze_transcript(transcript: str) -> dict:
    """Analyze a meeting transcript and return structured intelligence."""
    transcript_truncated = transcript[:4000]

    system_prompt = """You are a meeting intelligence analyst.
Analyze the meeting transcript and return ONLY valid JSON with these exact keys:
- summary: 2-3 sentence overview of the meeting
- action_items: list of dicts with keys: person, task, deadline
- decisions: list of decisions made during the meeting
- participants: list of people mentioned
- meeting_type: one of "standup", "planning", "review", "general"
"""

    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcript:\n{transcript_truncated}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    return json.loads(response.choices[0].message.content)


SAMPLE_TRANSCRIPT = """
John: Good morning everyone. Let's start the sprint planning.
Sarah: I'll take the user authentication feature. Should be done by Friday.
John: Great. Mike, can you handle the database migration?
Mike: Yes, I'll complete it by Wednesday.
Sarah: We decided to use PostgreSQL instead of MySQL for the new project.
John: Agreed. Also, we need to update the API documentation by end of next week. Tom, can you own that?
Tom: Sure, I'll have it done by next Friday.
John: Perfect. Let's also move our daily standup to 9am starting Monday.
Everyone: Agreed.
"""

if __name__ == "__main__":
    print("=== MEETING ANALYSIS ===")
    result = analyze_transcript(SAMPLE_TRANSCRIPT)

    print(f"Summary     : {result.get('summary')}")
    print(f"Participants: {result.get('participants')}")
    print(f"Meeting Type: {result.get('meeting_type')}")
    print(f"Decisions   : {result.get('decisions')}")
    print(f"Action Items:")
    for item in result.get('action_items', []):
        print(f"  - {item.get('person'):<8}: {item.get('task')} (by {item.get('deadline')})")