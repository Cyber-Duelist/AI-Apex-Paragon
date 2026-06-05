import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load the secret key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define the exact prompt from the curriculum
user_prompt = """You are a document risk analyst.
Write a detailed risk assessment report for this document:
'Merger Agreement, Legal dept, 105 pages, multiple authors, last edited 2 days ago'
Cover: risk level, key concerns, and recommended actions."""

print("=== STARTING STREAM ===\n")

# 3. Make the API Call with stream=True
stream = client.chat.completions.create(
    messages=[{"role": "user", "content": user_prompt}],
    model="llama-3.3-70b-versatile",
    # CRITICAL: This parameter tells the API to send chunks as they are generated
    stream=True, 
)

# 4. Iterate through the stream as tokens arrive over the network
for chunk in stream:
    # We must check if content exists, as the final chunk is usually empty
    if chunk.choices[0].delta.content is not None:
        # end="" prevents Python from printing a new line every time
        # flush=True forces the terminal to print instantly instead of buffering
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\n=== STREAM COMPLETE ===")