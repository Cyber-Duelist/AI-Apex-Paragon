# PersonaDoc

A production-grade RAG (Retrieval-Augmented Generation) system that ingests documents, indexes them in a persistent vector store, and answers questions grounded in the document content.

---

## What PersonaDoc Does

PersonaDoc takes any PDF or TXT document, chunks it into semantically meaningful pieces, stores those chunks in ChromaDB with full citation metadata, and retrieves the most relevant context to answer questions. A confidence gate prevents the LLM from hallucinating when the retrieved context is insufficient. An evaluation pipeline measures answer accuracy against a golden dataset.

---

## Tech Stack

`Python` · `FastAPI` · `ChromaDB` · `sentence-transformers` · `Groq` · `LLaMA 3.3 70B` · `pypdf` · `python-dotenv`

---

## Project Structure

| File | Purpose |
|---|---|
| `ingest.py` | Extract text from PDF and TXT files with page-level metadata |
| `chunker.py` | Split pages into overlapping chunks with citation metadata on every chunk |
| `vector_store.py` | ChromaDB persistent vector store — add, search, and delete chunks |
| `main.py` | FastAPI service — upload, search, and delete endpoints |
| `reranker.py` | Cross-encoder reranking for improved retrieval precision |
| `hallucination_control.py` | Confidence gate that refuses to answer when context is insufficient |
| `eval.py` | Golden dataset evaluation measuring retrieval and answer accuracy |

---

## How to Run

```bash
# Install dependencies
pip install pypdf chromadb sentence-transformers groq python-dotenv python-multipart

# Add your Groq API key to .env at project root
GROQ_API_KEY=your_key_here

# Start the API
uvicorn week_09.persona_doc.main:app --reload

# Visit
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload a PDF or TXT file and index it |
| POST | `/search` | Search indexed documents by natural language query |
| DELETE | `/delete` | Clear the entire vector store |

---

## How the RAG Pipeline Works

**Ingest** — Text is extracted from the uploaded document page by page. Each page carries source filename and page number as metadata.

**Chunk** — Pages are split into overlapping fixed-size chunks. Every chunk inherits the source metadata so the system always knows where each piece of text came from.

**Embed and Store** — Chunks are embedded using `all-MiniLM-L6-v2` and stored in ChromaDB. The store persists to disk so indexed documents survive restarts.

**Retrieve and Rerank** — At query time the question is embedded, ChromaDB returns the top matches by vector similarity, and a cross-encoder reranks them for precision.

**Generate with Guard** — Retrieved chunks are injected into a prompt. If the top chunk scores below the confidence threshold the system refuses to answer. Otherwise the LLM answers using only the retrieved context.

---

## Evaluation Results

Tested against 5 golden questions on the merger agreement document.

| Question | Expected | Result |
|---|---|---|
| When was the merger agreement signed? | January 10, 2024 | PASS |
| What premium will shareholders receive? | 15 percent | PASS |
| Where will disputes be settled? | Delaware | FAIL |
| What happens to Company B after completion? | wholly-owned subsidiary | PASS |
| Who approved the transaction? | board of directors | PASS |

```
Total questions : 5
Grounded        : 4
Correct         : 4
Accuracy        : 80.0%
```

Q3 failed because the Delaware chunk scored below the confidence threshold and the hallucination guard correctly refused to answer rather than guess.

---

## What I Learned

- Persistent vector storage with ChromaDB means the system does not need to re-embed documents on every restart — indexing once and querying many times is how production RAG systems work.
- Reranking adds a second pass of precision on top of vector similarity — the cross-encoder re-scores each retrieved chunk against the query and often changes the ranking, improving answer quality.
- A confidence gate that refuses to answer is not a failure — it is a feature. An 80% accurate system that says "I don't know" for the other 20% is far more trustworthy than one that hallucinates confident wrong answers.
