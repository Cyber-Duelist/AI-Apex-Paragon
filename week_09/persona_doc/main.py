import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

# Ensure Python can find our local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document
from chunker import chunk_document
from vector_store import get_collection, add_chunks, search, delete_collection

# 1. Initialize the FastAPI Application
app = FastAPI(title="PersonaDoc API", description="Production RAG API")

# Ensure the temporary uploads directory exists
UPLOAD_DIR = os.path.join(current_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 2. Initialize our Persistent Database Connection
collection = get_collection()

# 3. Define our Pydantic Data Models (Strict Input/Output validation)
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SearchResult(BaseModel):
    rank: int
    source: str
    page: int
    text: str

# 4. Define the Endpoints

@app.get("/")
def root():
    """Health check endpoint to ensure the API is alive."""
    return {"status": "PersonaDoc API is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a file upload, saves it to disk, extracts text, 
    chunks it, embeds it, and stores it in ChromaDB.
    """
    try:
        # Save the uploaded file temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Execute our RAG ingestion pipeline
        pages = ingest_document(file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="Failed to extract text from document.")
        
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

@app.post("/search", response_model=List[SearchResult])
def search_documents(req: SearchRequest):
    """
    Takes a natural language query, converts it to a vector, 
    and searches the ChromaDB database for the closest chunks.
    """
    # Query our database
    raw_results = search(req.query, collection, top_k=req.top_k)
    
    # Format the results strictly according to our Pydantic model
    formatted_results = []
    for idx, res in enumerate(raw_results, 1):
        formatted_results.append(
            SearchResult(
                rank=idx,
                source=res["metadata"]["source"],
                page=res["metadata"]["page"],
                text=res["text"]
            )
        )
    return formatted_results

@app.delete("/delete")
def delete_all():
    """Wipes the database cleanly."""
    delete_collection(collection)
    return {"status": "collection cleared"}