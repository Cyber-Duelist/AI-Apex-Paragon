import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    for base_url in ["https://api.deepseek.com", "https://api.deepseek.com/v1"]:
        print(f"Testing {base_url}...")
        client = AsyncOpenAI(api_key=os.getenv('DEEPSEEK1'), base_url=base_url)
        try:
            res = await client.chat.completions.create(model='deepseek-chat', messages=[{'role': 'user', 'content': 'hi'}])
            print(f"SUCCESS: {base_url} -> {res.choices[0].message.content}")
        except Exception as e:
            print(f"FAILED: {base_url} -> {e}")

asyncio.run(main())
