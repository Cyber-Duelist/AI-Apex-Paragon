import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document
from chunker import chunk_document
from vector_store import get_collection, add_chunks, search, delete_collection
from hallucination_control import rag_with_guard

app = FastAPI(title="PersonaDoc API", description="Production RAG API")

UPLOAD_DIR = os.path.join(current_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

collection = get_collection()

# Pydantic Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    source: Optional[str] = None

class Citation(BaseModel):
    source: str
    page: int

class SearchResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: List[Citation]

# Endpoints
@app.get("/")
def root():
    return {"status": "PersonaDoc API is running"}

@app.get("/documents")
def list_documents():
    """Lists all unique documents currently indexed in ChromaDB."""
    results = collection.get(include=["metadatas"])
    sources = list({m["source"] for m in results["metadatas"]}) if results["metadatas"] else []
    return {"documents": sources}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload any PDF or TXT file and index it."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = ingest_document(file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="Failed to extract text.")

        chunks = chunk_document(pages, chunk_size=400, overlap=80)
        add_chunks(chunks, collection)

        return {
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "indexed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/search", response_model=SearchResponse)
def search_documents(req: SearchRequest):
    """Ask a question. Get a cited, grounded answer."""
    result = rag_with_guard(req.query, collection)
    citations = []
    if result.get("grounded"):
        raw = search(req.query, collection, top_k=req.top_k)
        if req.source:
            raw = [r for r in raw if r["metadata"]["source"] == req.source]
        citations = [
            Citation(source=r["metadata"]["source"], page=r["metadata"]["page"])
            for r in raw
        ]

    return SearchResponse(
        question=req.query,
        answer=result["answer"],
        grounded=result["grounded"],
        citations=citations
    )

@app.delete("/delete")
def delete_all():
    delete_collection(collection)
    return {"status": "collection cleared"}