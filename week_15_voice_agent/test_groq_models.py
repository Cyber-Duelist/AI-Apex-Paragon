import os
import asyncio
from dotenv import load_dotenv
from groq import Groq

load_dotenv('.env')
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
models = client.models.list()
for m in models.data:
    if 'vision' in m.id.lower():
        print("Vision model found:", m.id)
