import asyncio
import os
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY_1') or os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
img = Image.new('RGB', (10, 10))

async def test_models():
    models = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-3.1-flash-lite', 'gemini-flash-lite-latest', 'gemini-2.5-flash', 'gemini-3.5-flash']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            await model.generate_content_async(['test', img])
            print(f'{m}: SUCCESS')
        except Exception as e:
            print(f'{m}: FAILED - {e}')

asyncio.run(test_models())
