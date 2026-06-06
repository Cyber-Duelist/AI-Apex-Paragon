import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer

# Ensure Python can find our previous modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document
from chunker import chunk_document

# 1. Load the embedding model globally
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_collection():
    """
    Creates or loads a persistent ChromaDB client saved to the local disk.
    Returns the 'persona_doc' collection (think of a collection like a SQL table).
    """
    db_path = os.path.join(current_dir, "chroma_db")
    # PersistentClient ensures data survives script restarts
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="persona_doc")
    return collection

def add_chunks(chunks: list[dict], collection):
    """
    Embeds the chunk text and saves it to ChromaDB alongside its provenance metadata.
    """
    if not chunks:
        return

    # Extract all the data we need into parallel lists (Chroma's preferred format)
    ids = [chunk["chunk_id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    
    # Clean up the metadata dicts to pass into Chroma
    metadatas = []
    for chunk in chunks:
        metadatas.append({
            "source": chunk["source"],
            "page": chunk["page"],
            "char_start": chunk["char_start"],
            "char_end": chunk["char_end"]
        })
        
    # Generate embeddings and convert PyTorch tensors to standard Python lists
    embeddings = model.encode(texts).tolist()

    # Insert into the database
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def search(query: str, collection, top_k: int = 3) -> list[dict]:
    """
    Embeds a user query, searches the database using Cosine Similarity,
    and returns the top matches with their original text and metadata.
    """
    query_embedding = model.encode([query]).tolist()
    
    # Chroma handles the Cosine Similarity math for us automatically!
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    formatted_results = []
    # Chroma returns lists of lists, so we access index 0
    if results and "documents" in results and results["documents"]:
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
            })
            
    return formatted_results

def delete_collection(collection):
    """
    Utility function to wipe the database so we don't accidentally duplicate
    chunks while testing.
    """
    existing_data = collection.get()
    if existing_data and existing_data["ids"]:
        collection.delete(ids=existing_data["ids"])


if __name__ == "__main__":
    target_file = os.path.join(current_dir, "sample.txt")
    
    # 1. Initialize the Database
    collection = get_collection()
    
    # Wipe it clean for our test
    delete_collection(collection)
    
    # 2. Ingest & Chunk (Using our previous code!)
    pages = ingest_document(target_file)
    production_chunks = chunk_document(pages, chunk_size=400, overlap=80)
    
    # 3. Add to Database
    print("=== ADDING TO VECTOR STORE ===")
    add_chunks(production_chunks, collection)
    print(f"Added {len(production_chunks)} chunks to ChromaDB.\n")
    
    # 4. Search the Database
    query = "What are the financial terms?"
    print(f"=== SEARCHING: {query} ===")
    
    search_results = search(query, collection, top_k=2)
    
    for idx, res in enumerate(search_results, 1):
        meta = res["metadata"]
        # Clean up text for the console
        clean_text = res["text"].replace('\n', ' ')
        
        print(f"Rank {idx} | Source: {meta['source']} | Page: {meta['page']}")
        print(f"Text: {clean_text[:80]}...\n")