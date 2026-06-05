import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load Environment
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define Pricing Dictionary (Cost per 1,000,000 tokens)
# Note: Groq pricing varies, but we use standard market rates for 70B models here.
PRICING = {
    "llama-3.3-70b-versatile": {
        "input_per_1m": 0.59,
        "output_per_1m": 0.79
    }
}

# 3. Cost Calculation Engine
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICING:
        return 0.0 # Return 0 if model is unknown
    
    # Convert per-million pricing to per-token pricing
    input_price_per_token = PRICING[model]["input_per_1m"] / 1_000_000
    output_price_per_token = PRICING[model]["output_per_1m"] / 1_000_000
    
    total_input_cost = input_tokens * input_price_per_token
    total_output_cost = output_tokens * output_price_per_token
    
    return total_input_cost + total_output_cost

# 4. Telemetry Wrapper
def tracked_call(prompt: str, model: str) -> dict:
    # Make the API Call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract telemetry
    text = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    # Calculate Cost
    call_cost = calculate_cost(model, input_tokens, output_tokens)
    
    return {
        "text": text.strip(),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": call_cost
    }

# 5. Execution Block
if __name__ == "__main__":
    MODEL_TO_USE = "llama-3.3-70b-versatile"
    
    prompts = [
        "Classify this in one word (low/medium/high): 'NDA, Legal, 2 pages'",
        "Write a two sentence risk summary for: 'Merger Agreement, Legal, 105 pages'",
        "List 3 risks for: 'Software License Agreement, IT dept, 48 pages'"
    ]
    
    total_session_cost = 0.0
    
    print("=== STARTING BATCH COST TRACKING ===\n")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"--- Prompt {i} ---")
        result = tracked_call(prompt, MODEL_TO_USE)
        
        print(f"Response: {result['text']}")
        print(f"Tokens: {result['input_tokens']} In | {result['output_tokens']} Out")
        # Print cost formatted to 6 decimal places because it will be fractions of a penny
        print(f"Cost: ${result['cost']:.6f}\n") 
        
        total_session_cost += result['cost']
        
    print("=============================")
    print(f"TOTAL SESSION COST: ${total_session_cost:.6f}")
    print("=============================")