from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List

# Import the bouncers we built in the last lesson
from pydantic_models import DocumentCreate, DocumentResponse

print("=== STARTING API SERVER ===")
app = FastAPI(title="Document AI API", version="1.0")

# Helper function to open the kitchen door safely
def get_db_connection():
    # Connect to the local database
    conn = sqlite3.connect("documents.db")
    # This magic line tells SQL to return rows as dictionaries (JSON) instead of basic tuples!
    conn.row_factory = sqlite3.Row
    return conn

# === ROUTE 1: GET (READ DATA) ===
# We tell FastAPI exactly what the output should look like (A List of DocumentResponses)
@app.get("/documents", response_model=List[DocumentResponse])
def get_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch everything from the kitchen
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert the SQL rows into a format FastAPI can send to the browser
    return [dict(row) for row in rows]

# === ROUTE 2: POST (WRITE NEW DATA) ===
# We force the incoming data to pass through the DocumentCreate bouncer
@app.get("/")
def home():
    return {"message": "Server is running! Go to /docs to test the API."}

@app.post("/documents", response_model=DocumentResponse)
def create_document(doc: DocumentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert the validated data into the database
    cursor.execute("""
        INSERT INTO documents (title, department, num_pages, high_risk, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (doc.title, doc.department, doc.num_pages, doc.high_risk, doc.created_at))
    
    # Save the changes
    conn.commit()
    
    # SQL automatically generates a new ID. We grab it here.
    new_id = cursor.lastrowid
    conn.close()
    
    # Combine the new ID with the user's data to send the final receipt back
    # Note: .model_dump() is how Pydantic v2 turns a model back into a dictionary
    response_data = doc.model_dump()
    response_data['id'] = new_id
    
    return response_data