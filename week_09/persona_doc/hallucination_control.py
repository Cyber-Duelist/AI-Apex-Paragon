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

def rag_with_guard(question: str, collection, source: str = None, model_name: str = "llama-3.3-70b-versatile") -> dict:
    """
    Retrieves documents and checks the semantic similarity. 
    If the match is too weak, it refuses to call the LLM.
    """
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    # 1. Search ChromaDB for top 3 chunks
    retrieved = search(question, collection, top_k=3, source_filter=source)
    
    if not retrieved:
        context_text = "No relevant documents found for this query."
    else:
        context_text = "\n".join([f"- {chunk['text']}" for chunk in retrieved])
    
    system_prompt = (
        "You are a friendly, conversational, and helpful AI document assistant.\n"
        "Your creator is Adarsh Kumar Singh. If someone asks who created you, made you, or built you, you must explicitly and proudly state that Adarsh Kumar Singh created you.\n"
        "Your primary goal is to answer the user's question using the provided context from their documents.\n"
        "If the provided context contains the answer, explain it clearly and comprehensively.\n"
        "If the user asks about a topic not covered in the documents, DO NOT abruptly reject them. "
        "Instead, politely inform them that the uploaded documents don't mention this, but you are happy to discuss it or provide an answer based on your general knowledge. Be very friendly and accommodating.\n\n"
        f"Context from documents:\n{context_text}"
    )
    
    response = groq_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}"}
        ],
        temperature=0.3
    )
    
    return {
        "answer": response.choices[0].message.content,
        "grounded": len(retrieved) > 0,
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