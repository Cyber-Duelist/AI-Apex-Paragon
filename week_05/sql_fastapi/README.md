# Document Management REST API 📄

**A lightweight, database-backed REST API for managing corporate documents and assessing risk.**

## What This Project Does
This microservice provides a fully functional backend for a document management system. It exposes a complete CRUD (Create, Read, Update, Delete) API that interacts directly with a local SQLite database. Incoming data is strictly validated to ensure database integrity before any records are written or modified.

## Tech Stack
* **Python**
* **FastAPI**
* **SQLite**
* **Pydantic**
* **Uvicorn**

## Project Structure
* `setup_db.py` - Initializes the database, builds the schema, and seeds it with mock data.
* `pydantic_models.py` - Defines strict data schemas and validation rules for incoming/outgoing API traffic.
* `crud.py` - The main FastAPI application routing HTTP requests to the SQL database.
* `documents.db` - The local SQLite database storing persistent records.

## API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| **GET** | `/documents` | Fetch all documents from the database |
| **POST** | `/documents` | Add a new document to the database |
| **PUT** | `/documents/{id}` | Update an existing document by its ID |
| **DELETE**| `/documents/{id}` | Delete a document permanently by its ID |

## How to Run

1. **Install the required dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic