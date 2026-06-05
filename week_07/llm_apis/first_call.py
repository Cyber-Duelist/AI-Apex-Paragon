import os
from dotenv import load_dotenv
from groq import Groq

# 1. LOad the secret key from the .env file.
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Defining or clearing the context.
document_info = "Merger Agreement, Legal dept, 105 pages"
user_prompt = f"You are a document risk analyst.\nGiven this document: '{document_info}',\nis it high risk? Answer in one sentence."

# 3. Make the API Call to Llama 3 via Groq's LPUs
chat_completion = client.chat.completions.create(
    messages=[{"role": "user", "content": user_prompt}],
    model="llama-3.3-70b-versatile",
)

# 4. Extract and print the response and token usage
print("=== LLM RESPONSE ===")
print(chat_completion.choices[0].message.content)

print("\n=== TOKEN USAGE ===")
print(f"Input tokens : {chat_completion.usage.prompt_tokens}")
print(f"Output tokens: {chat_completion.usage.completion_tokens}")