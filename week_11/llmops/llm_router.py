import os
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define our Model Tiers
FAST_MODEL = "llama-3.1-8b-instant"      # cheap, fast, simple tasks
SMART_MODEL = "llama-3.3-70b-versatile"   # powerful, slower, complex tasks

def classify_query(query: str) -> str:
    """
    Acts as the triage agent. Uses the cheapest model to determine query complexity.
    """
    system_prompt = """
    Classify this query as either 'simple' or 'complex'.
    Simple: greetings, basic facts, yes/no questions.
    Complex: analysis, reasoning, multi-step tasks, risk assessment.
    Reply with ONLY one word: simple or complex.
    """
    
    response = client.chat.completions.create(
        model=FAST_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.0, # Zero creativity, just strict classification
        max_tokens=10    # We only need one word, save tokens!
    )
    
    # Strip any accidental punctuation or whitespace the LLM might add
    return response.choices[0].message.content.strip().lower().replace('.', '')

def route_and_run(query: str) -> dict:
    """
    Classifies the query, selects the appropriate model, and executes the generation.
    """
    # Step 1: Triage
    classification = classify_query(query)
    
    # Step 2: Route
    # Default to the smart model just in case the classifier hallucinates
    target_model = FAST_MODEL if classification == "simple" else SMART_MODEL
    
    # Step 3: Execute
    response = client.chat.completions.create(
        model=target_model,
        messages=[{"role": "user", "content": query}],
        temperature=0.3
    )
    
    return {
        "query": query,
        "classification": classification,
        "model_used": target_model,
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens
    }

if __name__ == "__main__":
    print("=== INITIALIZING LLM ROUTER ===\n")
    
    # A mix of questions to test our router's intelligence
    test_queries = [
        "What is 2 + 2?",
        "Analyze the risk profile of a 200-page merger agreement from Legal.",
        "Hello, how are you today?",
        "Compare the macroeconomic impacts of inflation vs deflation over a 10-year horizon.",
        "Is the capital of France Paris?"
    ]
    
    for i, q in enumerate(test_queries, 1):
        print(f"=== QUERY {i} ===")
        result = route_and_run(q)
        
        print(f"Query     : {result['query']}")
        print(f"Category  : {result['classification']}")
        print(f"Model Used: {result['model_used']}")
        
        # Clean up the text for terminal formatting
        clean_response = result['response'].replace('\n', ' ')
        if len(clean_response) > 80:
            clean_response = clean_response[:80] + "..."
            
        print(f"Response  : {clean_response}")
        print(f"Tokens    : {result['tokens']}\n")