import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv('.env')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
vision_model = genai.GenerativeModel('gemini-2.5-flash')

async def test():
    # Create a dummy solid color image
    img = Image.new('RGB', (100, 100), color = 'red')
    try:
        response = await vision_model.generate_content_async(["What is this?", img])
        print("Success:", response.text)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
