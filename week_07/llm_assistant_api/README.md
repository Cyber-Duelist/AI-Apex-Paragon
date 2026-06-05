# LLM Assistant API

A FastAPI service that performs AI-powered document risk analysis using the Groq LLM API and LLaMA 3.3. Supports structured JSON analysis, live streaming reports, and per-call cost tracking.

---

## Tech Stack

- *FastAPI* — REST API framework
- *Groq* — LLM inference provider
- *LLaMA 3.3 70B Versatile* — language model
- *Pydantic* — request/response validation
- *python-dotenv* — environment config

---

## Project Structure


week_07/
  llm_assistant_api/
    main.py       # FastAPI app with all 3 endpoints
  llm_apis/
    first_call.py         # Basic LLM call
    structured_output.py  # JSON-mode outputs
    streaming.py          # Token-by-token streaming
    tool_calling.py       # Function/tool calling
    retries.py            # Retry with exponential backoff
    cost_tracker.py       # Token usage and cost tracking


---

## Setup

bash
# Clone the repo and enter project root
git clone https://github.com/your-username/AI-APEX-PARAGON.git
cd AI-APEX-PARAGON

# Activate virtual environment
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install fastapi uvicorn groq python-dotenv

# Add your Groq API key to .env at project root
GROQ_API_KEY=your_key_here


---

## Run Locally

bash
uvicorn week_07.llm_assistant_api.main:app --reload


API will be live at http://localhost:8000

---

## Endpoints

### GET /health
Returns service status and active model.

bash
curl http://localhost:8000/health


json
{
  "status": "ok",
  "model": "llama-3.3-70b-versatile"
}


---

### POST /analyze
Analyzes a document and returns structured risk data as JSON. Includes retry logic and cost tracking per call.

bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"document_title": "Merger Agreement", "department": "Legal", "num_pages": 105}'


json
{
  "document_title": "Merger Agreement",
  "department": "Legal",
  "risk_level": "high",
  "risk_score": 0.92,
  "reason": "Merger agreements involve complex legal and financial obligations that pose significant risk.",
  "input_tokens": 68,
  "output_tokens": 45,
  "cost_usd": 0.000076
}


---

### POST /analyze/stream
Streams a detailed risk assessment report token by token. Same request body as /analyze.

bash
curl -X POST http://localhost:8000/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"document_title": "Merger Agreement", "department": "Legal", "num_pages": 105}'


Response streams live to the terminal as the model generates it.

---

## Key Concepts Demonstrated

| Concept | Where |
|---|---|
| Structured JSON outputs | /analyze endpoint |
| Streaming responses | /analyze/stream endpoint |
| Retry with exponential backoff | Wrapped around /analyze LLM call |
| Cost tracking | Returned in every /analyze response |
| Tool calling | week_07/llm_apis/tool_calling.py |

---

## What I Would Improve Next

- Add a database to log every request, response, and cost over time
- Add authentication so the API is not open to anyone
- Add a /analyze/batch endpoint for multiple documents in one call
- Connect to PersonaDoc RAG pipeline for document upload and retrieval