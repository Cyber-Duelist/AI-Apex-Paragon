# Production Python — Backend Engineering Foundations

A production-grade FastAPI service built with proper engineering practices: environment config, structured logging, automated tests, and Docker containerization.

---

## What This Covers

This project goes beyond writing ML scripts. It applies the engineering patterns used in real backend systems — configuration management, observability, testing, and deployment — to a FastAPI document management service.

---

## Tech Stack

`Python` · `FastAPI` · `SQLite` · `Pydantic` · `pytest` · `Docker` · `python-dotenv`

---

## Project Structure

```
week_06/production_python/
│
├── env_setup.py        # Loads and validates environment variables from .env
├── logger_setup.py     # Configures logging to console and file with severity levels
├── test_api.py         # pytest test suite covering all 4 CRUD endpoints
├── Dockerfile          # Containerizes the FastAPI app with python:3.12-slim
├── requirements.txt    # All project dependencies
├── app.log             # Generated log file (created on first run)
├── .env                # Local environment config (never committed to GitHub)
└── README.md           # This file
```

> API source lives in `week_05/sql_fastapi/crud.py` and `pydantic_models.py`

---

## How to Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API
cd week_05/sql_fastapi
uvicorn crud:app --reload

# Visit
http://127.0.0.1:8000/documents
http://127.0.0.1:8000/docs
```

---

## How to Run with Docker

```bash
# Build the image
docker build -t document-risk-api .

# Run the container
docker run -p 8000:8000 document-risk-api

# Visit
http://127.0.0.1:8000/documents
```

---

## How to Run Tests

```bash
pytest week_06/production_python/test_api.py -v
```

Expected output:

```
test_get_documents_status PASSED
test_get_documents_returns_list PASSED
test_post_document PASSED
test_put_document PASSED
test_delete_document PASSED

5 passed in 0.96s
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/documents` | Fetch all documents |
| POST | `/documents` | Add a new document |
| PUT | `/documents/{id}` | Update a document by ID |
| DELETE | `/documents/{id}` | Delete a document by ID |

---

## What I Learned

- Hardcoding config values is a security risk — environment variables keep secrets out of your codebase and off GitHub.
- Logging with severity levels (DEBUG → CRITICAL) gives you visibility into what your app is doing without touching the code.
- A passing test suite means you can change code confidently — if tests still pass, you haven't broken anything.
