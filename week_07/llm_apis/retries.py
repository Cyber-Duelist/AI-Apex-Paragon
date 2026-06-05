import os
import time
from dotenv import load_dotenv
from groq import Groq
import groq # We need the base groq module to catch its specific errors

# 1. Load Environment and Initialize Client
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. The Robust Wrapper Function
def call_with_retry(prompt: str, max_retries: int = 3):
    """
    Calls the Groq API with an exponential backoff retry mechanism.
    If the API is busy or rate-limited, it will wait 2, 4, then 8 seconds before failing.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"=== ATTEMPT {attempt} ===")
            
            # Attempt the API Call
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # If successful, return the response immediately (breaking the loop)
            return response
            
        except (groq.RateLimitError, groq.APIStatusError, groq.APIConnectionError) as e:
            # If this was our last attempt, don't wait—just crash gracefully
            if attempt == max_retries:
                print(f"\n[FATAL] Max retries exhausted after {max_retries} attempts.")
                raise e
            
            # Calculate Exponential Backoff (2^1=2s, 2^2=4s, etc.)
            wait_time = 2 ** attempt
            print(f"[WARNING] API Error: {type(e).__name__}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)


# 3. Execution Block
if __name__ == "__main__":
    user_prompt = "Explain why exponential backoff is important in distributed systems in 2 short sentences."
    
    try:
        final_response = call_with_retry(user_prompt)
        
        print("\n=== FINAL RESPONSE ===")
        print(final_response.choices[0].message.content)
        
        print("\n=== TOKEN USAGE ===")
        print(f"Input:  {final_response.usage.prompt_tokens}")
        print(f"Output: {final_response.usage.completion_tokens}")
        
    except Exception as e:
        print("\nProcess failed. Check your logs.")