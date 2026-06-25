import os
import sys
from sentence_transformers import CrossEncoder

# Ensure Python can find our local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ingest import ingest_document
from chunker import chunk_document
from vector_store import get_collection, add_chunks, search, delete_collection

# 1. Initialize the Cross-Encoder model (It will download weights on the first run)
print("Loading Cross-Encoder model (this may take a moment)...")
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    """
    Takes a list of retrieved chunks from ChromaDB and re-scores them 
    against the query using a high-precision Cross-Encoder.
    """
    if not chunks:
        return []

    # The CrossEncoder expects data as a list of pairs: [[query, text1], [query, text2]]
    pairs = [[query, chunk["text"]] for chunk in chunks]
    
    # Calculate exact attention scores
    scores = cross_encoder.predict(pairs)
    
    # Attach the new scores to our original chunk dictionaries
    for i, chunk in enumerate(chunks):
        chunk["rerank_score"] = float(scores[i])
        
    # Sort the chunks based on the new Cross-Encoder score (highest first)
    reranked_chunks = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
    
    # Return only the top K results
    return reranked_chunks[:top_k]


if __name__ == "__main__":
    target_file = os.path.join(current_dir, "sample.txt")
    collection = get_collection()
    
    # 1. Run the Full Ingestion Flow
    delete_collection(collection) # Wipe clean for the test
    pages = ingest_document(target_file)
    chunks = chunk_document(pages, chunk_size=400, overlap=80)
    add_chunks(chunks, collection)
    
    query = "What are the financial terms?"
    
    # 2. Initial Vector Search (Fast, but sometimes inaccurate)
    # We ask for the top 5 here to cast a wide net
    initial_results = search(query, collection, top_k=5)
    
    print("\n=== BEFORE RERANKING (vector similarity order) ===")
    for idx, res in enumerate(initial_results, 1):
        clean_text = res["text"].replace('\n', ' ')
        print(f"Rank {idx}: {clean_text[:60]}...")
        
    # 3. Reranking (Slow, but highly precise)
    reranked_results = rerank(query, initial_results, top_k=3)
    
    print("\n=== AFTER RERANKING (cross-encoder order) ===")
    for idx, res in enumerate(reranked_results, 1):
        clean_text = res["text"].replace('\n', ' ')
        print(f"Rank {idx} (score: {res['rerank_score']:.4f}): {clean_text[:60]}...")