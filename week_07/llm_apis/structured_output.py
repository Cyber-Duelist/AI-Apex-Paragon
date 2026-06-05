import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Load the secret key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define the exact JSON schema we want
system_prompt = "You are a document risk analyst. You must respond ONLY with valid JSON, no explanation, no extra text."

user_prompt = """Analyze this document: 'Merger Agreement, Legal dept, 105 pages'
Return JSON with these exact keys:
- document_title
- department
- risk_level (low/medium/high)
- risk_score (0.0 to 1.0)
- reason (one sentence)"""

# 3. Make the API Call
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    model="llama-3.3-70b-versatile",
    # CRITICAL: This parameter forces the API to only return valid JSON
    response_format={"type": "json_object"},
)

# 4. Extract the raw string response
raw_response = chat_completion.choices[0].message.content

# 5. Convert the string into a real Python dictionary using json.loads()
try:
    parsed_data = json.loads(raw_response)
    
    print("=== STRUCTURED DOCUMENT ANALYSIS ===")
    print(f"Title      : {parsed_data.get('document_title')}")
    print(f"Department : {parsed_data.get('department')}")
    print(f"Risk Level : {parsed_data.get('risk_level')}")
    print(f"Risk Score : {parsed_data.get('risk_score')}")
    print(f"Reason     : {parsed_data.get('reason')}")
    
except json.JSONDecodeError:
    print("ERROR: LLM did not return valid JSON. Raw output:")
    print(raw_response)