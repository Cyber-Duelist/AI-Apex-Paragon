import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

async def test():
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Safely evaluates a math expression. Use this instead of guessing math answers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "The mathematical expression to calculate"}
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    try:
        completion = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hello, calculate 4 * 5"}],
            temperature=0.7,
            max_tokens=50,
            tools=tools,
            tool_choice="auto"
        )
        print("Success:", completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq API Error: {e}")

asyncio.run(test())
