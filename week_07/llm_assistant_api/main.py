import os
import json
import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import groq as groq_exceptions

# 1. Initialization
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI(title="LLM Assistant API")

MODEL_NAME = "llama-3.3-70b-versatile"
PRICING = {
    MODEL_NAME: {"input_per_1m": 0.59, "output_per_1m": 0.79}
}

# 2. Pydantic Models
class DocumentRequest(BaseModel):
    document_id: str
    title: str
    department: str
    num_pages: int

# 3. Helper Functions
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICING: return 0.0
    input_price = PRICING[model]["input_per_1m"] / 1_000_000
    output_price = PRICING[model]["output_per_1m"] / 1_000_000
    return (input_tokens * input_price) + (output_tokens * output_price)

def call_with_retry(messages: list, response_format: dict = None, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            kwargs = {
                "model": MODEL_NAME,
                "messages": messages
            }
            if response_format:
                kwargs["response_format"] = response_format
            return client.chat.completions.create(**kwargs)
        except (groq_exceptions.RateLimitError, groq_exceptions.APIStatusError, groq_exceptions.APIConnectionError) as e:
            if attempt == max_retries:
                raise HTTPException(status_code=503, detail=f"LLM API completely failed: {str(e)}")
            time.sleep(2 ** attempt)

# 4. API Endpoints
@app.get("/")
def root():
    return {"status": "LLM Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL_NAME}

@app.post("/analyze")
def analyze_document(doc: DocumentRequest):
    system_prompt = "You are a document risk analyst. You must respond ONLY with valid JSON, no explanation, no extra text."
    user_prompt = f"Analyze this document: '{doc.title}, {doc.department} dept, {doc.num_pages} pages'. Return JSON with these exact keys: document_id, title, risk_level (low/medium/high), risk_score (0.0 to 1.0), reason (one sentence), tokens_used."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = call_with_retry(messages=messages, response_format={"type": "json_object"})

    try:
        parsed_data = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse LLM output as JSON.")

    parsed_data["document_id"] = doc.document_id
    parsed_data["tokens_used"] = response.usage.total_tokens
    parsed_data["session_cost"] = round(calculate_cost(MODEL_NAME, response.usage.prompt_tokens, response.usage.completion_tokens), 6)

    return parsed_data

@app.post("/analyze/stream")
def analyze_document_stream(doc: DocumentRequest):
    user_prompt = f"You are a document risk analyst. Write a detailed risk assessment report for this document: '{doc.title}, {doc.department} dept, {doc.num_pages} pages'. Cover: risk level, key concerns, and recommended actions."

    def generate_stream():
        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": user_prompt}],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n[STREAM FAILED: {str(e)}]"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")