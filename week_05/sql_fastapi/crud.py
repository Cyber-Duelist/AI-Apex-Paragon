from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List

# Import our Pydantic bouncers
from pydantic_models import DocumentCreate, DocumentResponse

print("=== STARTING FULL CRUD API SERVER ===")
app = FastAPI(title="Document AI API - Full CRUD", version="1.0")

# Helper function to open the kitchen door safely
def get_db_connection():
    conn = sqlite3.connect("documents.db")
    conn.row_factory = sqlite3.Row
    return conn

# === 1. READ (GET) ===
@app.get("/documents", response_model=List[DocumentResponse])
def get_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# === 2. CREATE (POST) ===
@app.post("/documents", response_model=DocumentResponse)
def create_document(doc: DocumentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (title, department, num_pages, high_risk, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (doc.title, doc.department, doc.num_pages, doc.high_risk, doc.created_at))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    response_data = doc.model_dump()
    response_data['id'] = new_id
    return response_data

# === 3. UPDATE (PUT) ===
@app.put("/documents/{id}", response_model=DocumentResponse)
def update_document(id: int, doc: DocumentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Attempt to update the specific row
    cursor.execute("""
        UPDATE documents 
        SET title = ?, department = ?, num_pages = ?, high_risk = ?, created_at = ?
        WHERE id = ?
    """, (doc.title, doc.department, doc.num_pages, doc.high_risk, doc.created_at, id))
    
    # If rowcount is 0, it means that ID doesn't exist in our database!
    if cursor.rowcount == 0:
        conn.close()
        # Raise a 404 Error to tell the frontend the document wasn't found
        raise HTTPException(status_code=404, detail="Document not found")
        
    conn.commit()
    conn.close()
    
    # Send back the updated data with its ID
    response_data = doc.model_dump()
    response_data['id'] = id
    return response_data

# === 4. DELETE (DELETE) ===
@app.delete("/documents/{id}")
def delete_document(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Attempt to delete the specific row
    cursor.execute("DELETE FROM documents WHERE id = ?", (id,))
    
    # If rowcount is 0, the ID didn't exist
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
        
    conn.commit()
    conn.close()
    
    # Send a success confirmation back to the frontend
    return {"message": f"Document {id} deleted successfully"}