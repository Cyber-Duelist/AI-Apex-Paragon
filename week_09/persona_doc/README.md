# PersonaDoc

A production-grade RAG (Retrieval-Augmented Generation) system that ingests documents, indexes them in a persistent vector store, and answers questions grounded in the document content.

---

## What PersonaDoc Does

PersonaDoc takes any PDF or TXT document, chunks it into semantically meaningful pieces, stores those chunks in ChromaDB with full citation metadata, and retrieves the most relevant context to answer questions. It features a complete **"Shiny Black" Glassmorphism Web Interface** where users can chat with their documents, hot-swap between multiple LLMs (Llama 3, Qwen, Allam), target specific documents, and export their conversation history. A confidence gate prevents the LLM from hallucinating when the retrieved context is insufficient.

---

`Python` · `FastAPI` · `ChromaDB` · `sentence-transformers` · `Groq` · `Vanilla JS/CSS (Glassmorphism)` · `marked.js`

---

## Project Structure

| File | Purpose |
|---|---|
| `ingest.py` | Extract text from PDF and TXT files with page-level metadata |
| `chunker.py` | Split pages into overlapping chunks with citation metadata on every chunk |
| `vector_store.py` | ChromaDB persistent vector store — add, search, and delete chunks |
| `main.py` | FastAPI service — upload, search, and delete endpoints + Static File Server |
| `static/index.html` | The "Shiny Black" Chat Dashboard |
| `static/style.css` | Glassmorphism styles and Premium UI definitions |
| `static/app.js` | Frontend logic for API calls, markdown rendering, and local storage |
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
uvicorn main:app --port 8081

# Visit the Dashboard
http://127.0.0.1:8081/
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Serves the frontend web dashboard |
| GET | `/documents` | Lists all currently indexed documents |
| POST | `/upload` | Upload a PDF or TXT file and index it |
| POST | `/search` | Search indexed documents (supports Targeted Search & Model Switching) |
| DELETE | `/documents/{filename}` | Permanently scrub a document from the local disk and ChromaDB |

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

- Persistent vector storage with ChromaDB means the system does not need to re-embed documents on every restart.
- Building a full-stack dashboard over an API drastically improves usability, especially with features like Targeted Search which allows users to restrict vector retrieval to a single `source` file.
- "Soft Deletes" are not enough for secure document systems. Deleting a file requires physically wiping the PDF and scrubbing its embeddings from the vector database.
- Chat history persistence (via `localStorage`) and markdown rendering (via `marked.js`) are essential for a premium conversational UI.
