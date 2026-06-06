import os
import sys
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import util

# Ensure Python can find our local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the model directly from vector_store so we don't load it twice
from vector_store import get_collection, search, model

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def rag_with_guard(question: str, collection, threshold: float = 0.25) -> dict:
    """
    Retrieves documents and checks the semantic similarity. 
    If the match is too weak, it refuses to call the LLM.
    """
    # 1. Search ChromaDB for top 3 chunks
    retrieved = search(question, collection, top_k=3)
    
    if not retrieved:
        return {
            "answer": "I don't have enough information.", 
            "grounded": False, 
            "reason": "No relevant context found in database"
        }
        
    # 2. Check the similarity score of the top result
    top_text = retrieved[0]["text"]
    
    # Calculate exact Cosine Similarity between the question and the best chunk
    query_emb = model.encode(question)
    doc_emb = model.encode(top_text)
    top_score = util.cos_sim(query_emb, doc_emb)[0][0].item()
    
    # 3. The Confidence Gate
    if top_score < threshold:
        return {
            "answer": "I don't have enough information.", 
            "grounded": False, 
            "reason": f"No relevant context found (Score: {top_score:.4f} is below threshold {threshold})"
        }
        
    # 4. If above threshold, build prompt and call LLM
    context_text = "\n".join([f"- {chunk['text']}" for chunk in retrieved])
    
    system_prompt = (
        "You are a strict document analyst. Answer the user's question using ONLY the provided context.\n"
        f"Context:\n{context_text}"
    )
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"}
        ],
        temperature=0.0
    )
    
    return {
        "answer": response.choices[0].message.content,
        "grounded": True,
        "chunks_used": len(retrieved)
    }

if __name__ == "__main__":
    collection = get_collection()
    
    tests = [
        "What are the financial terms of the merger?",
        "What is the weather in Tokyo?",
        "Who approved the transaction?"
    ]
    
    for q in tests:
        print(f"=== Q: {q} ===")
        res = rag_with_guard(q, collection)
        print(f"Grounded: {res['grounded']}")
        print(f"Answer: {res['answer']}\n")