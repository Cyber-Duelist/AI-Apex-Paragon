import os
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer, util

# 1. Load environment variables (Make sure your .env has GROQ_API_KEY)
load_dotenv()

# 2. Initialize Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Create our Knowledge Base (10 chunks simulating a real document)
chunks = [
    "This merger agreement outlines the definitive terms under which Company A will acquire Company B.",
    "It was officially signed and executed on January 10, 2024.",
    "Shareholders of Company B will receive a 15 percent premium on their current stock valuation.",
    "The target closing date for the acquisition is set for the third quarter of this fiscal year.",
    "Both parties agree to the financial terms and regulatory stipulations detailed herein.",
    "Upon completion, Company B will operate as a wholly-owned subsidiary of Company A.",
    "Legal compliance teams have initiated the antitrust review process with federal regulators in Washington D.C.",
    "We anticipate a smooth transition; Company B employees will retain their current healthcare benefits and seniority for at least 12 months.",
    "Any disputes arising from this document will be settled through binding arbitration in Delaware.",
    "This document supersedes any prior communications or letters of intent between the parties."
]

def build_vector_store(chunks):
    """Embeds all chunks and stores them in our in-memory database."""
    embeddings = embedding_model.encode(chunks)
    vector_store = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        vector_store.append({
            "id": i + 1,
            "text": chunk,
            "embedding": emb
        })
    return vector_store

def retrieve(query, vector_store, top_k=3):
    """Finds the most mathematically similar chunks to the user's query."""
    query_embedding = embedding_model.encode(query)
    
    # PRO-TIP: Using np.array() here fixes the PyTorch speed warning you saw earlier!
    store_embeddings = np.array([item["embedding"] for item in vector_store])
    
    cosine_scores = util.cos_sim(query_embedding, store_embeddings)[0]
    
    results = []
    for i, score in enumerate(cosine_scores):
        results.append({
            "score": score.item(),
            "text": vector_store[i]["text"]
        })
        
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def rag_query(question, vector_store):
    """The Complete RAG Loop: Retrieve, Inject, and Generate."""
    # Step 1: Retrieve the top 3 relevant chunks
    top_chunks = retrieve(question, vector_store, top_k=3)
    
    # Step 2: Combine those chunks into a single string
    context_text = "\n".join([f"- {chunk['text']}" for chunk in top_chunks])
    
    # Step 3: Build the strict system prompt
    system_prompt = (
        "You are a document analyst. Answer the question using ONLY the context below.\n"
        "If the answer is not in the context, say 'I don't have enough information.'\n\n"
        f"Context:\n{context_text}"
    )
    
    # Step 4: Call the LLM
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"}
        ],
        temperature=0.0 # Set to 0 to prevent hallucinations
    )
    
    answer = response.choices[0].message.content
    return answer, top_chunks

# Execute the Pipeline
if __name__ == "__main__":
    print("=== INITIALIZING RAG PIPELINE ===")
    vector_store = build_vector_store(chunks)
    print(f"Successfully embedded and stored {len(vector_store)} chunks.")
    print("=================================\n")
    
    test_queries = [
        "What is the closing date for the acquisition?",
        "What happens to Company B employees?",
        "What are the antitrust requirements?"
    ]
    
    for q in test_queries:
        print(f"=== QUERY: {q} ===")
        answer, retrieved = rag_query(q, vector_store)
        
        print("Retrieved Chunks:")
        for i, chunk in enumerate(retrieved, 1):
            print(f"  {i}. {chunk['text']} (Score: {chunk['score']:.4f})")
            
        print(f"\nLLM Answer:\n{answer}")
        print("===================================================\n")