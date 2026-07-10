from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
import urllib.request
import urllib.parse
from dotenv import load_dotenv
import edge_tts
from groq import AsyncGroq
from pathlib import Path
import google.generativeai as genai
import base64
from io import BytesIO
from PIL import Image

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Omni-Modal Voice Agent API")
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
vision_model = genai.GenerativeModel(
    'gemini-flash-latest',
    system_instruction="You are a highly precise visual AI. Identify objects literally and accurately. Do not guess, make jokes, or assume it is a trick. Keep responses under 2 sentences."
)

conversation_history = [
    {"role": "system", "content": "You are Entropy, a helpful, extremely concise, and witty AI assistant. Keep responses under 2 sentences to ensure fast voice generation."}
]

def search_wikipedia(query: str) -> str:
    """Searches Wikipedia for real-time information."""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            results = data.get("query", {}).get("search", [])
            if results:
                snippet = results[0]["snippet"].replace('<span class="searchmatch">', '').replace('</span>', '')
                import re
                snippet = re.sub('<[^<]+>', '', snippet)
                return f"Wikipedia top result for '{query}': {snippet}"
            return "No results found on Wikipedia."
    except Exception as e:
        return f"Search failed: {e}"

def get_weather(city: str) -> str:
    """Fetches real-time weather using wttr.in"""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            temp = data['current_condition'][0]['temp_C']
            desc = data['current_condition'][0]['weatherDesc'][0]['value']
            return f"Weather in {city}: {temp}°C, {desc}."
    except Exception as e:
        return f"Weather search failed: {e}"

def get_crypto_price(coin_id: str) -> str:
    """Fetches crypto price using CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={urllib.parse.quote(coin_id.lower())}&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            if coin_id.lower() in data:
                price = data[coin_id.lower()]["usd"]
                return f"The current price of {coin_id} is ${price} USD."
            return f"Coin '{coin_id}' not found."
    except Exception as e:
        return f"Crypto search failed: {e}"

def calculate(expression: str) -> str:
    """Safely evaluates a math expression"""
    try:
        import ast
        import operator
        allowed_operators = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                             ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
        def eval_expr(node):
            if isinstance(node, ast.Constant): return node.value
            elif isinstance(node, ast.Num): return node.n # For older python versions
            elif isinstance(node, ast.BinOp): return allowed_operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp): return allowed_operators[type(node.op)](eval_expr(node.operand))
            else: raise TypeError(node)
        result = eval_expr(ast.parse(expression, mode='eval').body)
        return f"Result of {expression} is {result}"
    except Exception as e:
        return f"Calculation failed: {e}"

def get_news(topic: str) -> str:
    """Fetches top news headlines using Google News RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('utf-8')
            import re
            titles = re.findall(r'<title>(.*?)</title>', xml_data)
            headlines = titles[1:4] if len(titles) > 1 else []
            if headlines:
                return f"Top news for '{topic}': " + "; ".join(headlines)
            return f"No news found for '{topic}'."
    except Exception as e:
        return f"News search failed: {e}"

def get_stock_price(ticker: str) -> str:
    """Fetches stock price using Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker.upper())}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            result = data.get("chart", {}).get("result", [])
            if result:
                price = result[0]["meta"]["regularMarketPrice"]
                return f"The current stock price of {ticker.upper()} is ${price}."
            return f"Ticker '{ticker}' not found."
    except Exception as e:
        return f"Stock search failed: {e}"

async def analyze_vision(query: str, base64_data: str) -> str:
    """Passes a webcam frame to Gemini Vision to answer a visual query."""
    try:
        encoded_data = base64_data.split(",")[1] if "," in base64_data else base64_data
        image_data = base64.b64decode(encoded_data)
        img = Image.open(BytesIO(image_data))
        response = await vision_model.generate_content_async([query, img])
        return response.text
    except Exception as e:
        return f"Vision analysis failed: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Searches Wikipedia for real-time information about people, places, concepts, or recent events if you don't know the answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetches real-time weather data for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The name of the city, e.g., 'New York', 'Tokyo'"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Fetches the current real-time USD price of a cryptocurrency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "coin_id": {"type": "string", "description": "The ID of the coin, e.g., 'bitcoin', 'ethereum', 'dogecoin'"}
                },
                "required": ["coin_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Safely evaluates a math expression. Use this instead of guessing math answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The mathematical expression to calculate, e.g., '25 * 4', '(100 - 30) / 2'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Fetches the latest top news headlines for a specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The news topic, e.g., 'technology', 'artificial intelligence', 'politics'"}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Fetches the current real-time price of a stock using its ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "The stock ticker symbol, e.g., 'AAPL' for Apple, 'TSLA' for Tesla"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "look_at_webcam",
            "description": "Uses the agent's computer vision to look at the webcam frame and answer questions about the user's surroundings or objects they are holding.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The specific question to ask the vision model about the frame."}
                },
                "required": ["query"]
            }
        }
    }
]

@app.get("/")
async def get_frontend():
    with open(Path(__file__).parent / "index.html", "r") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/stream")
async def websocket_audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to Omni-Modal Pipeline")
    
    current_task = None
    latest_frame_base64 = None
    
    async def speak_text(text: str):
        if not text.strip(): return
        try:
            communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
            audio_data = bytearray()
            async for tts_chunk in communicate.stream():
                if tts_chunk["type"] == "audio":
                    audio_data.extend(tts_chunk["data"])
            if audio_data:
                await websocket.send_bytes(bytes(audio_data))
        except Exception as e:
            print(f"TTS Error: {e}")

    async def generate_response(user_text):
        nonlocal latest_frame_base64
        await websocket.send_text(json.dumps({"type": "clear"}))
        
        model_name = "llama-3.1-8b-instant"
        msg_content = user_text
        print("Using Groq Brain Omni-Modal Pipeline")
            
        temp_messages = conversation_history + [{"role": "user", "content": msg_content}]
        
        try:
            stream_completion = None
            tool_calls = None
            response_message = None
            
            # Text model: First do a non-streaming call to check if the LLM wants to use a tool
            completion = await groq_client.chat.completions.create(
                model=model_name,
                messages=temp_messages,
                temperature=0.7,
                max_tokens=200,
                tools=tools,
                tool_choice="auto"
            )
            response_message = completion.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                func_name = tool_calls[0].function.name
                print(f"Agent requested tool: {func_name}")
                await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": f"[Executing {func_name}...] "}))
                
                args = json.loads(tool_calls[0].function.arguments)
                tool_result = ""
                
                if func_name == "search_wikipedia":
                    tool_result = search_wikipedia(args.get("query", ""))
                elif func_name == "get_weather":
                    tool_result = get_weather(args.get("city", ""))
                elif func_name == "get_crypto_price":
                    tool_result = get_crypto_price(args.get("coin_id", ""))
                elif func_name == "calculate":
                    tool_result = calculate(args.get("expression", ""))
                elif func_name == "get_news":
                    tool_result = get_news(args.get("topic", ""))
                elif func_name == "get_stock_price":
                    tool_result = get_stock_price(args.get("ticker", ""))
                elif func_name == "look_at_webcam":
                    if latest_frame_base64:
                        tool_result = await analyze_vision(args.get("query", "Describe what is in front of the camera."), latest_frame_base64)
                        latest_frame_base64 = None
                    else:
                        tool_result = "No webcam frame is currently available."
                else:
                    tool_result = "Tool not recognized."
                    
                print(f"Tool Result: {tool_result}")
                
                temp_messages.append(response_message)
                temp_messages.append({
                    "tool_call_id": tool_calls[0].id,
                    "role": "tool",
                    "name": func_name,
                    "content": tool_result,
                })
                
                # Stream the final response after the tool result is injected
                stream_completion = await groq_client.chat.completions.create(
                    model=model_name,
                    messages=temp_messages,
                    temperature=0.7,
                    max_tokens=150,
                    stream=True
                )
            else:
                # No tool called, just stream a normal response to save latency
                stream_completion = await groq_client.chat.completions.create(
                    model=model_name,
                    messages=temp_messages,
                    temperature=0.7,
                    max_tokens=150,
                    stream=True
                )
                
            llm_response = ""
            sentence_buffer = ""
            
            if stream_completion:
                async for chunk in stream_completion:
                    token = chunk.choices[0].delta.content or ""
                    llm_response += token
                    sentence_buffer += token
                    
                    if token:
                        await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": token}))
                        
                    if any(p in token for p in ['.', '!', '?', '\n']):
                        await speak_text(sentence_buffer.strip())
                        sentence_buffer = ""
                        
                if sentence_buffer.strip():
                    await speak_text(sentence_buffer.strip())
                    
            conversation_history.append({"role": "user", "content": user_text})
            conversation_history.append({"role": "assistant", "content": llm_response})
            print(f"Entropy: {llm_response}")
            
        except asyncio.CancelledError:
            print("Generation interrupted.")
            raise
        except Exception as e:
            print(f"Pipeline Error: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("type") == "vision_frame":
                latest_frame_base64 = payload.get("image", "")
                
            elif payload.get("type") == "user_speech":
                user_text = payload.get("text", "")
                print(f"User: {user_text}")
                
                if current_task and not current_task.done():
                    current_task.cancel()
                    
                current_task = asyncio.create_task(generate_response(user_text))
                
            elif payload.get("type") == "interrupt":
                if current_task and not current_task.done():
                    current_task.cancel()
                    
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Socket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
