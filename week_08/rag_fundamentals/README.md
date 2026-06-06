# RAG Fundamentals

A from-scratch implementation of Retrieval-Augmented Generation (RAG) — from raw text to embeddings, vector search, and LLM-powered answers grounded in retrieved context.

---

## What This Covers

The four building blocks of every RAG system: generating embeddings, chunking documents, searching by semantic similarity, and combining retrieval with an LLM to produce grounded answers.

---

## Tech Stack

`Python` · `sentence-transformers` · `Groq` · `LLaMA 3.3 70B` · `python-dotenv`

---

## Project Structure

| File | Purpose |
|---|---|
| `embeddings.py` | Generate 384-dimensional vectors from text and compute cosine similarity |
| `chunking.py` | Split documents using fixed-size overlap and sentence-based strategies |
| `vector_search.py` | Build an in-memory vector store and retrieve top-K chunks by similarity |
| `rag_pipeline.py` | Full pipeline — embed corpus, retrieve context, answer questions with LLM |

---

## How RAG Works

**Step 1 — Embed**
Every document chunk is converted into a vector of numbers using a sentence transformer model. Similar text produces similar vectors.

**Step 2 — Retrieve**
When a question comes in, it is also embedded. Cosine similarity finds the chunks whose vectors are closest to the question vector — these are the most relevant pieces of context.

**Step 3 — Generate**
The retrieved chunks are injected into a prompt alongside the question. The LLM answers using only that context — grounded in real documents, not hallucination.

---

## Results — RAG Pipeline Answers

**Q: What is the closing date for the acquisition?**
> The target closing date for the acquisition is set for the third quarter of this fiscal year.

**Q: What happens to Company B employees?**
> Company B employees will retain their current healthcare benefits and seniority for at least 12 months after the completion of the operation.

**Q: What are the antitrust requirements?**
> I don't have enough information.

The third answer demonstrates correct RAG behavior — when the context does not contain enough detail, the LLM says so instead of hallucinating an answer.

---

## How to Run

```bash
# Install dependencies
pip install sentence-transformers groq python-dotenv

# Run each component individually
python embeddings.py
python chunking.py
python vector_search.py
python rag_pipeline.py
```

Make sure `GROQ_API_KEY` is set in your `.env` file at the project root.

---

## What I Learned

- Embeddings turn text into math — and that math captures meaning. Two sentences about the same topic land close together in vector space even if they share no words.
- Chunking strategy matters. Overlap between chunks preserves context at boundaries, which improves retrieval quality for questions that span multiple sentences.
- A well-built RAG system should refuse to answer when the context is insufficient. "I don't have enough information" is a correct answer, not a failure.
