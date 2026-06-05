import sys
import os
from fastapi.testclient import TestClient

# === SYSTEM PATHING HACK (UPDATED) ===
# 1. Get the absolute paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
week5_dir = os.path.join(root_dir, 'week_05', 'sql_fastapi')

# 2. Add BOTH the root folder and the week_05 folder to Python's brain
sys.path.insert(0, root_dir)
sys.path.insert(0, week5_dir)  # <-- THIS FIXES THE IMPORT ERROR

# 3. Change working directory so SQLite finds 'documents.db'
os.chdir(week5_dir)

# Now we can safely import the Waiter (app) we built
from crud import app

# Create a fake browser (TestClient) to simulate sending requests to our API
client = TestClient(app)


print("\n=== STARTING AUTOMATED TEST SUITE ===\n")

# TEST 1: Check if the GET route successfully responds
def test_get_documents_status():
    response = client.get("/documents")
    assert response.status_code == 200

# TEST 2: Check if the GET route returns a JSON List
def test_get_documents_returns_list():
    response = client.get("/documents")
    assert isinstance(response.json(), list)

# TEST 3: Check if the POST route correctly creates a document
def test_post_document():
    new_doc = {
        "title": "Automated Pytest Doc",
        "department": "Engineering",
        "num_pages": 5,
        "high_risk": 0,
        "created_at": "2024-06-05"
    }
    response = client.post("/documents", json=new_doc)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Automated Pytest Doc"

# TEST 4: Check if the PUT route correctly updates a document
def test_put_document():
    # A. Create a temporary document first
    temp_doc = {"title": "Temp", "department": "HR", "num_pages": 1, "high_risk": 0, "created_at": "2024-06-05"}
    post_resp = client.post("/documents", json=temp_doc)
    doc_id = post_resp.json()["id"] # Grab its ID
    
    # B. Update that exact document
    updated_doc = temp_doc.copy()
    updated_doc["title"] = "Updated by Pytest"
    
    put_resp = client.put(f"/documents/{doc_id}", json=updated_doc)
    assert put_resp.status_code == 200
    assert put_resp.json()["title"] == "Updated by Pytest"

# TEST 5: Check if the DELETE route successfully removes a document
def test_delete_document():
    # A. Create a document specifically to destroy it
    doom_doc = {"title": "Doomed Doc", "department": "Legal", "num_pages": 10, "high_risk": 1, "created_at": "2024-06-05"}
    post_resp = client.post("/documents", json=doom_doc)
    doc_id = post_resp.json()["id"]
    
    # B. Destroy it
    del_resp = client.delete(f"/documents/{doc_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == f"Document {doc_id} deleted successfully"