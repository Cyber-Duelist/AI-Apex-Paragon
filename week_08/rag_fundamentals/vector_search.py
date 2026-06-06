import numpy as np
from sentence_transformers import SentenceTransformer, util

# 1. Load the embedding model (This will load instantly from your cache this time)
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Create our knowledge base (8 distinct chunks across different corporate topics)
chunks = [
    # Finance / Merger
    "Shareholders of Company B will receive a 15 percent premium on their current stock valuation.",
    "Both parties agree to the financial terms and regulatory stipulations detailed herein.",
    "The target closing date for the acquisition is set for the third quarter of this fiscal year.",
    # Legal / Compliance
    "Legal compliance teams have initiated the antitrust review process with federal regulators.",
    "Any disputes arising from this document will be settled through binding arbitration in Delaware.",
    "This document supersedes any prior communications or letters of intent between the parties.",
    "A recent internal audit revealed three minor compliance violations regarding data retention.",
    # HR
    "The new employee handbook outlines the remote work policy and updated PTO accrual rates."
]

print("=== INITIALIZING VECTOR STORE ===")
# 3. Embed all chunks and store them in our "database" (a list of dictionaries)
vector_store = []
chunk_embeddings = model.encode(chunks)

for i, (chunk, emb) in enumerate(zip(chunks, chunk_embeddings)):
    vector_store.append({
        "id": i + 1,
        "text": chunk,
        "embedding": emb
    })
print(f"Successfully embedded and stored {len(vector_store)} chunks.\n")

# 4. Define the Search Engine
def search(query, top_k=3):
    # Convert the user's text question into a vector
    query_embedding = model.encode(query)
    
    # Extract all the document vectors from our store into a single list
    store_embeddings = np.array([item["embedding"] for item in vector_store])
    
    # Calculate cosine similarity between the query and ALL documents simultaneously
    cosine_scores = util.cos_sim(query_embedding, store_embeddings)[0]
    
    # Pair each score with its corresponding text chunk
    results = []
    for i, score in enumerate(cosine_scores):
        results.append({
            "score": score.item(), # Extract the raw float from the PyTorch tensor
            "text": vector_store[i]["text"]
        })
        
    # Sort the results by score in descending order (highest similarity first)
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Return only the top requested results
    return results[:top_k]

# 5. Execute the required searches
queries = [
    "What are the financial terms of the merger?",
    "Are there any compliance or legal violations?"
]

for q in queries:
    print(f"=== SEARCH: {q} ===")
    top_results = search(q, top_k=3)
    for rank, res in enumerate(top_results, 1):
        print(f"Rank {rank} (score: {res['score']:.4f}): {res['text']}")
    print()