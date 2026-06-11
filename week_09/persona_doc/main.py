import os
import sys
import shutil
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document
from chunker import chunk_document
from vector_store import get_collection, add_chunks, search, delete_collection
from hallucination_control import rag_with_guard

app = FastAPI(title="PersonaDoc API", description="Production RAG API")

API_KEY = os.getenv("API_KEY", "supersecretkey")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

UPLOAD_DIR = os.path.join(current_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

collection = get_collection()

# Pydantic Models
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    source: Optional[str] = None
    model_name: Optional[str] = "llama-3.3-70b-versatile"

class Citation(BaseModel):
    source: str
    page: int

class SearchResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: List[Citation]

# Endpoints
STATIC_DIR = os.path.join(current_dir, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/documents", dependencies=[Depends(get_api_key)])
def list_documents():
    """Returns a list of unique document sources."""
    logger.info("Listing documents")
    results = collection.get(include=["metadatas"])
    if not results or not results.get("metadatas"):
        return {"documents": []}
    sources = set([meta["source"] for meta in results["metadatas"] if "source" in meta])
    return {"documents": list(sources)}

@app.delete("/documents/{filename}", dependencies=[Depends(get_api_key)])
def delete_document(filename: str):
    """Deletes a document from the vector store and the file system."""
    try:
        # Delete from ChromaDB
        collection.delete(where={"source": filename})
        
        # Delete from local file system
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        logger.info(f"Deleted document: {filename}")
        return {"message": f"Successfully deleted {filename}"}
    except Exception as e:
        logger.error(f"Error deleting {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.post("/upload", dependencies=[Depends(get_api_key)])
def upload_document(file: UploadFile = File(...)):
    """Upload any supported file and index it. Runs in a threadpool to prevent blocking."""
    try:
        logger.info(f"Received file upload: {file.filename}")
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = ingest_document(file_path)
        if not pages:
            logger.error(f"Failed to extract text from {file.filename}. Likely a scanned or image-based PDF.")
            raise HTTPException(status_code=400, detail="Could not extract text. The document might be scanned, image-based, or corrupted. Please upload a text-searchable file.")

        chunks = chunk_document(pages, chunk_size=400, overlap=80)
        add_chunks(chunks, collection)
        
        logger.info(f"Successfully indexed {file.filename} with {len(chunks)} chunks.")
        return {
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "indexed"
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/search", response_model=SearchResponse, dependencies=[Depends(get_api_key)])
def search_documents(req: SearchRequest):
    """Ask a question. Get a cited, grounded answer."""
    logger.info(f"Searching for query: {req.query}")
    # Pass the user's selected document to filter the RAG context
    result = rag_with_guard(req.query, collection, source=req.source, model_name=req.model_name)
    citations = []
    if result.get("grounded"):
        # Retrieve the exact citations used
        raw = search(req.query, collection, top_k=req.top_k, source_filter=req.source)
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

@app.delete("/delete", dependencies=[Depends(get_api_key)])
def delete_all():
    logger.info("Clearing entire collection")
    delete_collection(collection)
    return {"status": "collection cleared"}