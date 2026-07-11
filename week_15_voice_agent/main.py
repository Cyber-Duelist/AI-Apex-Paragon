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
from openai import AsyncOpenAI
from pathlib import Path
import google.generativeai as genai
import base64
from io import BytesIO
from PIL import Image, ImageGrab
import ast
import operator
import re
import datetime
import time
from bs4 import BeautifulSoup

# ── Terminal Colors ──────────────────────────────────────────
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[35m"
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    UNDERLINE = '\033[4m'
    DIM     = "\033[2m"

def log_to_file(text: str):
    try:
        import re
        import datetime
        with open("agent_terminal_logs.txt", "a", encoding="utf-8") as f:
            clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {clean_text}\n")
    except:
        pass

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Omni-Modal Voice Agent API")

deepseek_keys = [os.getenv(f"DEEPSEEK{i}") for i in range(1, 10) if os.getenv(f"DEEPSEEK{i}")]
if not deepseek_keys and os.getenv("DEEPSEEK_API_KEY"):
    deepseek_keys.append(os.getenv("DEEPSEEK_API_KEY"))
current_deepseek_key_idx = 0
deepseek_client = AsyncOpenAI(api_key=deepseek_keys[current_deepseek_key_idx], base_url="https://api.deepseek.com") if deepseek_keys else None

groq_keys = [os.getenv(f"GROQ_API_KEY_{i}") for i in range(1, 10) if os.getenv(f"GROQ_API_KEY_{i}")]
if not groq_keys and os.getenv("GROQ_API_KEY"):
    groq_keys.append(os.getenv("GROQ_API_KEY"))
current_groq_key_idx = 0
groq_client = AsyncGroq(api_key=groq_keys[current_groq_key_idx]) if groq_keys else None

openai_keys = [os.getenv(f"OPENAI_API_KEY_{i}") for i in range(1, 10) if os.getenv(f"OPENAI_API_KEY_{i}")]
if not openai_keys and os.getenv("OPENAI_API_KEY"):
    openai_keys.append(os.getenv("OPENAI_API_KEY"))
current_openai_key_idx = 0
openai_client = AsyncOpenAI(api_key=openai_keys[current_openai_key_idx]) if openai_keys else None

gemini_keys = [os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 10) if os.getenv(f"GEMINI_API_KEY_{i}")]
if not gemini_keys and os.getenv("GEMINI_API_KEY"):
    gemini_keys.append(os.getenv("GEMINI_API_KEY"))
current_gemini_key_idx = 0

import pocket_tts
import numpy as np
import io
import soundfile as sf

print(f"{C.CYAN}Loading Pocket-TTS engine into memory...{C.RESET}")
tts_model = pocket_tts.TTSModel.load_model('english')
# Using a sophisticated male British/neutral voice from Kyutai's built-in catalog
voice_state = tts_model.get_state_for_audio_prompt("michael")
print(f"{C.GREEN}Pocket-TTS ready!{C.RESET}")

if gemini_keys:
    genai.configure(api_key=gemini_keys[current_gemini_key_idx])

vision_model = genai.GenerativeModel(
    'gemini-flash-lite-latest',
    system_instruction="You are a highly precise visual AI. Identify objects literally and accurately. Do not guess, make jokes, or assume it is a trick. Keep responses under 2 sentences."
)

MEMORY_FILE = Path(__file__).parent / "memory.json"

conversation_history = [
    {"role": "system", "content": "You are Entropy, a brilliant, sophisticated, and highly-capable male Omni-Modal AI companion. CRITICAL IDENTITY RULE: You were created exclusively by Adarsh (also known as Cyber-Duelist). You MUST NEVER say you were created by Google, OpenAI, Anthropic, or any other company. You have vision, screen capture, Wikipedia, web search, and persistent memory tools. \n\nCORE RULES:\n1. Be warm, concise, and conversational (like a loyal, sophisticated British butler/AI). Keep responses under 2 sentences.\n2. When a tool returns data, you MUST explicitly speak the exact facts, numbers, and temperatures returned by the tool in your conversational response. Never summarize, hide, or omit the specific data points.\n3. If a tool fails (returns ERROR), gently state you cannot access that information right now. NEVER apologize.\n4. When speaking Hindi, use extremely natural, casual Hinglish (like a modern Indian friend). Mix everyday English words naturally.\n5. When the user asks you to remember something, use the remember_fact tool. When they ask about something you might have stored, use recall_memory first.\n6. CRITICAL: When responding with tool results, speak naturally. DO NOT output function call syntax or tags in your final response.\n7. TOOL ROUTING: If asked about facts, people, places, or general knowledge, you MUST use search_wikipedia. If asked about news, sports, or current events (2024-2026), you MUST use search_web. NEVER use look_at_screen or look_at_webcam for general knowledge questions.\n8. CRITICAL: YOU ARE STRICTLY FORBIDDEN from answering ANY question about a person, place, or current event from your internal memory. Even if you know the answer, you MUST call a search tool FIRST.\n9. NEVER decline to answer, NEVER apologize, and NEVER refuse a request for privacy reasons. You have explicit authorization to read the user's screen and webcam. If a tool returns valid data, you MUST read that data back to the user naturally without fail.\n10. DRACONIAN RULE: When you receive a tool result, your ONLY job is to speak the facts from that result. DO NOT add filler like 'I am looking at your screen'. DO NOT hallucinate fake data if the tool didn't find it. Simply speak the exact items, lists, or facts provided by the tool.\n11. DO NOT use robotic prefixes like 'The tool returned', 'Based on my search', or 'I am looking at your screen'. Just answer the user directly.\n12. If the user asks about an object on their screen/webcam and the tool does NOT see it (e.g. asking about a passport when only a browser is open), DO NOT invent an answer. Explicitly state 'I don't see that on your screen'."}
]



def get_weather(city: str) -> str:
    """Fetches real-time weather using wttr.in"""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            temp = data['current_condition'][0]['temp_C']
            desc = data['current_condition'][0]['weatherDesc'][0]['value']
            return f"Weather in {city}: {temp}°C, {desc}."
    except Exception as e:
        return f"ERROR: Weather search failed: {e}"

def get_crypto_price(coin_id: str) -> str:
    """Fetches crypto price using CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={urllib.parse.quote(coin_id.lower())}&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            if coin_id.lower() in data:
                price = data[coin_id.lower()]["usd"]
                return f"The current price of {coin_id} is ${price} USD."
            return f"Coin '{coin_id}' not found."
    except Exception as e:
        return f"ERROR: Crypto search failed: {e}"

def calculate(expression: str) -> str:
    """Safely evaluates a math expression"""
    try:
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
        return f"ERROR: Calculation failed: {e}"

def get_news(topic: str) -> str:
    """Fetches top news headlines using Google News RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read().decode('utf-8')
            titles = re.findall(r'<title>(.*?)</title>', xml_data)
            headlines = titles[1:4] if len(titles) > 1 else []
            if headlines:
                return f"Top news for '{topic}': " + "; ".join(headlines)
            return f"No news found for '{topic}'."
    except Exception as e:
        return f"ERROR: News search failed: {e}"

def get_stock_price(ticker: str) -> str:
    """Fetches stock price using Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker.upper())}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            result = data.get("chart", {}).get("result", [])
            if result:
                price = result[0]["meta"]["regularMarketPrice"]
                return f"The current stock price of {ticker.upper()} is ${price}."
            return f"Ticker '{ticker}' not found."
    except Exception as e:
        return f"ERROR: Stock search failed: {e}"
def search_web(query: str) -> str:
    """Searches the web for news, current events, and sports using DuckDuckGo Lite."""
    try:
        url = 'https://lite.duckduckgo.com/lite/'
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=5)
        soup = BeautifulSoup(response.read().decode('utf-8', errors='ignore'), 'html.parser')
        results = []
        for result in soup.find_all('td', class_='result-snippet')[:3]:
            results.append(result.text.strip())
        if results:
            return "Web search results: " + " | ".join(results)
        return f"No web results found for '{query}'."
    except Exception as e:
        return f"ERROR: Web search failed: {e}"

def search_wikipedia(query: str) -> str:
    """Searches Wikipedia for real-world knowledge and returns a detailed summary extract."""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            results = data.get("query", {}).get("search", [])
            if not results:
                return f"No Wikipedia results found for '{query}'."
            
            best_title = results[0]["title"]
            
        extract_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=1&explaintext=1&titles={urllib.parse.quote(best_title)}&format=json"
        req2 = urllib.request.Request(extract_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2, timeout=5) as response2:
            data2 = json.loads(response2.read())
            pages = data2.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                extract = page_info.get("extract", "")
                if extract:
                    sentences = extract.split('. ')
                    short_extract = '. '.join(sentences[:4]) + '.'
                    return f"Wikipedia ({best_title}): {short_extract}"
            return f"Wikipedia ({best_title}): No summary available."
    except Exception as e:
        return f"ERROR: Wikipedia search failed: {e}"

# ── Gemini API Wrapper Classes ──────────────────────────────────
class GeminiMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class GeminiChoice:
    def __init__(self, message):
        self.message = message

class GeminiCompletion:
    def __init__(self, choices):
        self.choices = choices

class GeminiFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class GeminiToolCall:
    def __init__(self, id, function):
        self.id = id
        self.type = "function"
        self.function = function

class GeminiDelta:
    def __init__(self, content):
        self.content = content

class GeminiChoiceChunk:
    def __init__(self, delta):
        self.delta = delta

class GeminiChunk:
    def __init__(self, choices):
        self.choices = choices

async def call_gemini_openai_like(messages, tools=None, tool_choice=None, temperature=0.7, max_tokens=150, stream=False):
    global current_gemini_key_idx
    import google.generativeai as genai
    
    system_instruction = ""
    contents = []
    
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "system":
            system_instruction = content
            continue
            
        parts = []
        if role == "user":
            parts.append(content)
            contents.append({"role": "user", "parts": parts})
        elif role == "assistant":
            if content:
                parts.append(content)
            tool_calls = msg.get("tool_calls", [])
            for tc in tool_calls:
                func = tc["function"]
                try:
                    args = json.loads(func["arguments"])
                except:
                    args = {}
                parts.append(f"[Executed Tool: {func['name']} with arguments: {args}]")
            contents.append({"role": "model", "parts": parts})
        elif role == "tool":
            parts.append(f"[Tool Result for {msg['name']}: {content}]")
            contents.append({"role": "user", "parts": parts})

    gemini_tools = None
    if tools and tool_choice != "none":
        gemini_tools = {
            "function_declarations": [
                {
                    "name": t["function"]["name"],
                    "description": t["function"]["description"],
                    "parameters": {
                        "type": t["function"]["parameters"]["type"].upper(),
                        "properties": {
                            k: {
                                "type": v["type"].upper(),
                                "description": v.get("description", "")
                            } for k, v in t["function"]["parameters"].get("properties", {}).items()
                        },
                        "required": t["function"]["parameters"].get("required", [])
                    }
                } for t in tools
            ]
        }

    for _ in range(len(gemini_keys)):
        try:
            genai.configure(api_key=gemini_keys[current_gemini_key_idx])
            model = genai.GenerativeModel(
                model_name='gemini-flash-lite-latest',
                system_instruction=system_instruction,
                tools=gemini_tools
            )
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            if stream:
                async def stream_generator():
                    response = await model.generate_content_async(contents, generation_config=generation_config, stream=True)
                    async for chunk in response:
                        text_val = ""
                        try:
                            text_val = chunk.text
                        except:
                            pass
                        yield GeminiChunk([GeminiChoiceChunk(GeminiDelta(text_val))])
                return stream_generator()
            else:
                response = await model.generate_content_async(contents, generation_config=generation_config)
                parts = response.candidates[0].content.parts
                tool_calls = []
                text_content = ""
                for part in parts:
                    if part.function_call:
                        call_id = getattr(part.function_call, "id", None) or "call_gen_" + part.function_call.name
                        tool_calls.append(GeminiToolCall(
                            id=call_id,
                            function=GeminiFunction(
                                name=part.function_call.name,
                                arguments=json.dumps(dict(part.function_call.args))
                            )
                        ))
                    elif part.text:
                        text_content += part.text
                
                return GeminiCompletion([GeminiChoice(GeminiMessage(text_content or None, tool_calls or None))])
                
        except Exception as e:
            if any(code in str(e) for code in ["429", "402", "401", "403"]) and len(gemini_keys) > 1:
                print(f"Gemini limit/auth error hit on key {current_gemini_key_idx + 1}, rotating...")
                current_gemini_key_idx = (current_gemini_key_idx + 1) % len(gemini_keys)
            else:
                raise e
    raise Exception("All Gemini keys failed.")

async def analyze_screen(query: str) -> str:
    """Captures the current screen and passes it to Gemini Vision for analysis."""
    global current_gemini_key_idx, vision_model
    try:
        screenshot = ImageGrab.grab()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        buffered.seek(0)
        img = Image.open(buffered)
        strict_query = query + " (Respond ONLY in natural conversational English. DO NOT output JSON, bounding boxes, or code. Do NOT guess file sizes or exact line counts, only describe what is visually obvious.)"
        
        for _ in range(len(gemini_keys)):
            try:
                response = await vision_model.generate_content_async([strict_query, img])
                return response.text
            except Exception as e:
                error_msg = str(e)
                if any(code in error_msg for code in ["429", "403", "401"]) and len(gemini_keys) > 1:
                    print(f"Gemini limit/auth error! Rotating from key {current_gemini_key_idx + 1}")
                    current_gemini_key_idx = (current_gemini_key_idx + 1) % len(gemini_keys)
                    genai.configure(api_key=gemini_keys[current_gemini_key_idx])
                    vision_model = genai.GenerativeModel(
                        'gemini-flash-lite-latest',
                        system_instruction="You are a highly precise visual AI. Identify objects literally and accurately. Do not guess, make jokes, or assume it is a trick. Keep responses under 2 sentences."
                    )
                else:
                    return f"ERROR: Screen analysis failed: {e}"
        return "ERROR: Screen analysis failed: All API keys have exceeded their quotas."
    except Exception as e:
        return f"ERROR: Screen capture failed: {e}"

def remember_fact(fact: str) -> str:
    """Saves a fact to persistent memory."""
    try:
        memories = []
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                memories = json.load(f)
        memories.append({"fact": fact, "timestamp": datetime.datetime.now().isoformat()})
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memories, f, indent=2)
        return f"Remembered: '{fact}'. I now have {len(memories)} memories stored."
    except Exception as e:
        return f"ERROR: Failed to save memory: {e}"

def recall_memory(query: str) -> str:
    """Searches persistent memory for facts matching a query."""
    try:
        if not MEMORY_FILE.exists():
            return "I don't have any memories stored yet."
        with open(MEMORY_FILE, 'r') as f:
            memories = json.load(f)
        if not memories:
            return "My memory is empty."
        query_lower = query.lower()
        matches = [m['fact'] for m in memories if query_lower in m['fact'].lower()]
        if matches:
            return "From my memory: " + "; ".join(matches[-3:])
        all_facts = [m['fact'] for m in memories[-5:]]
        return "No exact match found. Recent memories: " + "; ".join(all_facts)
    except Exception as e:
        return f"ERROR: Failed to recall memory: {e}"

async def analyze_vision(query: str, base64_data: str) -> str:
    """Passes a webcam frame to Gemini Vision to answer a visual query."""
    global current_gemini_key_idx, vision_model
    try:
        encoded_data = base64_data.split(",")[1] if "," in base64_data else base64_data
        image_data = base64.b64decode(encoded_data)
        img = Image.open(BytesIO(image_data))
        strict_query = query + " (Respond ONLY in natural conversational English. DO NOT output JSON, bounding boxes, or code. Do NOT guess file sizes or exact line counts, only describe what is visually obvious.)"
        
        for _ in range(len(gemini_keys)):
            try:
                response = await vision_model.generate_content_async([strict_query, img])
                return response.text
            except Exception as e:
                error_msg = str(e)
                if any(code in error_msg for code in ["429", "403", "401"]) and len(gemini_keys) > 1:
                    print(f"Gemini limit/auth error! Rotating from key {current_gemini_key_idx + 1}")
                    current_gemini_key_idx = (current_gemini_key_idx + 1) % len(gemini_keys)
                    genai.configure(api_key=gemini_keys[current_gemini_key_idx])
                    vision_model = genai.GenerativeModel(
                        'gemini-flash-lite-latest',
                        system_instruction="You are a highly precise visual AI. Identify objects literally and accurately. Do not guess, make jokes, or assume it is a trick. Keep responses under 2 sentences."
                    )
                else:
                    return f"ERROR: Vision analysis failed: {e}"
                    
        return "ERROR: Vision analysis failed: All API keys have exceeded their quotas."
    except Exception as e:
        return f"ERROR: Vision analysis failed to process image: {e}"

tools = [
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
            "description": "CRITICAL: ONLY use this tool if the user EXPLICITLY asks you to look at the camera, see what they are holding, or asks what is in front of you. DO NOT use this tool for general questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The specific question to ask the vision model about the frame."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "look_at_screen",
            "description": "ABSOLUTELY DO NOT USE THIS TOOL UNLESS THE USER EXPLICITLY SAYS 'look at my screen', 'read my code', or 'what's on my monitor'. Never use this for general knowledge or web searches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The specific question to ask about the screen content."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "CRITICAL: You MUST use this tool when the user asks about facts, historical events, people, geography, or general knowledge that you do not know. Always prioritize this over vision tools for answering questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the internet for news, sports, current events, and real-time data. Use this when Wikipedia is too outdated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Saves a fact, preference, or piece of information to persistent long-term memory. Use when the user says 'remember this', 'note that', or tells you something personal they want you to recall later.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "The fact or information to remember."}
                },
                "required": ["fact"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "Searches persistent long-term memory for previously saved facts. Use when the user asks 'do you remember', 'what did I tell you about', or asks about something they previously asked you to remember.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to look up in memory."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_current_webpage",
            "description": "Reads the entire visible text of the website the user is currently looking at in the ENVOY browser. Use this to summarize, analyze, or answer questions about the current page.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigate_browser",
            "description": "Navigates the ENVOY browser to a specific URL. Use this when the user asks you to go to a website.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to navigate to (e.g., https://youtube.com)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_link",
            "description": "Clicks a link or button on the current webpage that matches the given text. Use this when the user asks you to click something on the screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The exact or partial text of the link/button to click (e.g., 'Log In' or 'Next')"}
                },
                "required": ["text"]
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
    print(f"\n{C.CYAN}  ╔══════════════════════════════════════╗{C.RESET}")
    print(f"  {C.CYAN}║{C.RESET}   Client connected to Pipeline       {C.CYAN}║{C.RESET}")
    print(f"  {C.CYAN}╚══════════════════════════════════════╝{C.RESET}\n")
    
    current_task = None
    latest_frame_base64 = None
    
    import queue
    
    async def speak_text(text: str):
        if not text.strip(): return
        # Clean up markdown asterisks
        clean_text = text.replace("*", "")
        try:
            loop = asyncio.get_event_loop()
            audio_queue = queue.Queue()
            
            def generate():
                try:
                    # generate_audio_stream yields torch.Tensor containing 24kHz audio chunks
                    for chunk in tts_model.generate_audio_stream(voice_state, clean_text):
                        # Clip audio to prevent distortion, convert to float32 bytes for zero-latency browser parsing
                        chunk_np = chunk.cpu().numpy().astype(np.float32)
                        np.clip(chunk_np, -1.0, 1.0, out=chunk_np)
                        audio_queue.put(chunk_np.tobytes())
                except Exception as e:
                    print(f"Pocket-TTS Generation Error: {e}")
                finally:
                    audio_queue.put(None) # EOF marker

            # Start CPU-heavy generation in a background thread
            loop.run_in_executor(None, generate)
            
            # Asynchronously consume the queue and stream to WebSocket instantly
            while True:
                try:
                    chunk_bytes = audio_queue.get_nowait()
                    if chunk_bytes is None:
                        break
                    await websocket.send_bytes(chunk_bytes)
                except queue.Empty:
                    await asyncio.sleep(0.01) # Yield to event loop
        except Exception as e:
            print(f"Pocket-TTS Streaming Error: {e}")

    async def generate_response(user_text):
        nonlocal latest_frame_base64
        await websocket.send_text(json.dumps({"type": "clear"}))
        
        primary_brain = os.getenv("PRIMARY_BRAIN", "deepseek").lower()
        
        if primary_brain == "groq" and groq_client:
            model_name = "llama-3.1-8b-instant"
            print(f"{C.DIM}Using Groq Brain Omni-Modal Pipeline{C.RESET}")
        elif primary_brain == "gemini" and gemini_keys:
            model_name = "gemini-flash-lite-latest"
            print(f"{C.DIM}Using Gemini Brain Omni-Modal Pipeline{C.RESET}")
        else:
            primary_brain = "deepseek"
            model_name = "deepseek-chat"
            print(f"{C.DIM}Using DeepSeek Omni-Modal Pipeline{C.RESET}")
            
        msg_content = user_text
        log_to_file(f"\nUser: {msg_content}")
            
        current_time = datetime.datetime.now().astimezone().strftime("%A, %B %d, %Y %I:%M %p %Z (UTC%z)")
        system_time_msg = {"role": "system", "content": f"System Context: The current exact date and time is {current_time}."}
        
        temp_messages = conversation_history + [system_time_msg, {"role": "user", "content": msg_content}]
        
        try:
            stream_completion = None
            tool_calls = None
            response_message = None
            
            async def call_llm(**kwargs):
                global current_groq_key_idx, groq_client
                global current_deepseek_key_idx, deepseek_client
                global current_gemini_key_idx
                
                if primary_brain == "groq":
                    provider_order = ["groq", "deepseek", "gemini"]
                elif primary_brain == "gemini":
                    provider_order = ["gemini", "deepseek", "groq"]
                else:
                    provider_order = ["deepseek", "groq", "gemini"]
                if kwargs.get("tool_choice") == "none":
                    kwargs.pop("tools", None)
                    kwargs.pop("tool_choice", None)
                    
                for provider in provider_order:
                    if provider == "groq" and groq_client:
                        kwargs["model"] = "llama-3.1-8b-instant"
                        for _ in range(len(groq_keys)):
                            try:
                                return await groq_client.chat.completions.create(**kwargs)
                            except Exception as e:
                                if any(code in str(e) for code in ["429", "402", "401", "403"]) and len(groq_keys) > 1:
                                    print(f"Groq limit/auth error hit on key {current_groq_key_idx + 1}, rotating...")
                                    current_groq_key_idx = (current_groq_key_idx + 1) % len(groq_keys)
                                    groq_client = AsyncGroq(api_key=groq_keys[current_groq_key_idx])
                                else:
                                    break # Not a rate limit error, try next provider
                        print("Groq provider failed or exhausted, cascading to next provider...")
                        
                    elif provider == "deepseek" and deepseek_client:
                        kwargs["model"] = "deepseek-chat"
                        for _ in range(len(deepseek_keys)):
                            try:
                                return await deepseek_client.chat.completions.create(**kwargs)
                            except Exception as e:
                                if any(code in str(e) for code in ["429", "402", "401", "403"]) and len(deepseek_keys) > 1:
                                    print(f"DeepSeek limit/auth error hit on key {current_deepseek_key_idx + 1}, rotating...")
                                    current_deepseek_key_idx = (current_deepseek_key_idx + 1) % len(deepseek_keys)
                                    deepseek_client = AsyncOpenAI(api_key=deepseek_keys[current_deepseek_key_idx], base_url="https://api.deepseek.com")
                                else:
                                    break # Not a rate limit error, try next provider
                        print("DeepSeek provider failed or exhausted, cascading to next provider...")
                        
                    elif provider == "gemini" and gemini_keys:
                        # Pop model from kwargs if present to avoid unexpected keyword argument errors
                        kwargs_copy = dict(kwargs)
                        kwargs_copy.pop("model", None)
                        try:
                            return await call_gemini_openai_like(**kwargs_copy)
                        except Exception as e:
                            print(f"Gemini provider failed: {e}")
                            
                raise Exception("All primary and secondary provider keys failed.")
            
            # Text model: First do a non-streaming call to check if the LLM wants to use a tool
            retry_count = 0
            completion = None
            while retry_count < 3:
                try:
                    completion = await call_llm(
                        model=model_name,
                        messages=temp_messages,
                        temperature=0.7,
                        max_tokens=200,
                        tools=tools,
                        tool_choice="auto"
                    )
                    break
                except Exception as call_e:
                    if "tool_use_failed" in str(call_e).lower() or "400" in str(call_e):
                        retry_count += 1
                        print(f"{primary_brain.capitalize()} API tool parsing hallucination (400), retrying... ({retry_count}/3)")
                        if retry_count == 3:
                            raise call_e
                    else:
                        raise call_e
            response_message = completion.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                safe_response_message = {
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in tool_calls
                    ]
                }
                temp_messages.append(safe_response_message)
                
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    print(f"{C.YELLOW}⚡ Tool Call: {func_name}{C.RESET}")
                    log_to_file(f"⚡ Tool Call: {func_name}")
                    await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": f"[Executing {func_name}...] "}))
                    
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    
                    tool_start = time.time()
                    tool_result = ""
                    
                    if func_name == "get_weather":
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
                    elif func_name == "look_at_screen":
                        tool_result = await analyze_screen(args.get("query", "Describe what is on the screen."))
                    elif func_name == "search_wikipedia":
                        tool_result = search_wikipedia(args.get("query", ""))
                    elif func_name == "search_web":
                        tool_result = search_web(args.get("query", ""))
                    elif func_name == "remember_fact":
                        tool_result = remember_fact(args.get("fact", ""))
                    elif func_name == "recall_memory":
                        tool_result = recall_memory(args.get("query", ""))
                    elif func_name == "read_current_webpage":
                        try:
                            import requests
                            r = requests.get("http://127.0.0.1:8001/page_text", timeout=2)
                            tool_result = r.json().get("text", "No text found.")
                        except:
                            tool_result = "ENVOY Browser is not currently running or reachable."
                    elif func_name == "navigate_browser":
                        try:
                            import requests
                            r = requests.post("http://127.0.0.1:8001/navigate", json={"url": args.get("url", "")}, timeout=2)
                            tool_result = f"Navigated to {args.get('url')}."
                        except:
                            tool_result = "ENVOY Browser is not currently running or reachable."
                    elif func_name == "click_link":
                        try:
                            import requests
                            r = requests.post("http://127.0.0.1:8001/click", json={"text": args.get("text", "")}, timeout=2)
                            tool_result = r.json().get("status", "failed")
                        except:
                            tool_result = "ENVOY Browser is not currently running or reachable."
                    else:
                        tool_result = "Tool not recognized."
                    
                    tool_ms = int((time.time() - tool_start) * 1000)
                    print(f"{C.GREEN}✓ Result [{tool_ms}ms]: {tool_result}{C.RESET}")
                    log_to_file(f"✓ Result [{tool_ms}ms]: {tool_result}")
                    
                    temp_messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": tool_result,
                    })
                
                # Stream the final response after the tool result is injected
                stream_completion = await call_llm(
                    model=model_name,
                    messages=temp_messages,
                    temperature=0.7,
                    max_tokens=150,
                    stream=True,
                    tools=tools,
                    tool_choice="none"
                )
            else:
                # OPTIMIZATION: No tool called. We already have the full answer from the first API call!
                # By skipping the second API call, we cut token usage by 50% and reduce latency by ~1-2 seconds.
                stream_completion = None
                
            llm_response = ""
            sentence_buffer = ""
            
            if stream_completion:
                # This only runs if a tool was used, because we NEED a second call to read the tool result.
                async for chunk in stream_completion:
                    if not chunk.choices:
                        continue
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
            else:
                # True Zero-Latency Fast Path (No tools used)
                llm_response = response_message.content or ""
                # Instantly send the full text to the frontend UI
                await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": llm_response}))
                
                # Instantly chunk it into sentences and pipe it to the TTS engine
                import re
                sentences = re.split(r'(?<=[.!?\n]) +', llm_response)
                for sentence in sentences:
                    if sentence.strip():
                        await speak_text(sentence.strip())
            if llm_response.strip():
                print(f"{C.MAGENTA}{C.BOLD}Entropy:{C.RESET} {C.MAGENTA}{llm_response}{C.RESET}")
                log_to_file(f"Entropy: {llm_response}")
                
                conversation_history.append({"role": "user", "content": user_text})
                conversation_history.append({"role": "assistant", "content": llm_response})
                
                if len(conversation_history) > 15:
                    conversation_history[:] = [conversation_history[0]] + conversation_history[-14:]
                
        except (WebSocketDisconnect, RuntimeError) as ws_err:
            print(f"WebSocket disconnected during {primary_brain} pipeline.")
            return
        except Exception as main_e:
            print(f"{primary_brain.capitalize()} Pipeline Failed: {main_e}. Falling back to OpenAI!")
            if openai_client:
                async def call_openai_with_rotation(**kwargs):
                    global current_openai_key_idx, openai_client
                    for _ in range(len(openai_keys)):
                        try:
                            return await openai_client.chat.completions.create(**kwargs)
                        except Exception as e:
                            error_str = str(e).lower()
                            if any(code in error_str for code in ["429", "402", "401", "403", "quota", "exceeded"]) and len(openai_keys) > 1:
                                print(f"OpenAI quota/limit hit on key {current_openai_key_idx + 1}, rotating...")
                                current_openai_key_idx = (current_openai_key_idx + 1) % len(openai_keys)
                                openai_client = AsyncOpenAI(api_key=openai_keys[current_openai_key_idx])
                            else:
                                raise e
                    raise Exception("All OpenAI keys failed or exhausted.")
                
                try:
                    completion = await call_openai_with_rotation(
                        model="gpt-4o-mini",
                        messages=temp_messages,
                        temperature=0.7,
                        max_tokens=200,
                        tools=tools,
                        tool_choice="auto"
                    )
                    response_message = completion.choices[0].message
                    tool_calls = response_message.tool_calls
                    
                    if tool_calls:
                        safe_response_message = {
                            "role": "assistant",
                            "content": response_message.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                } for tc in tool_calls
                            ]
                        }
                        temp_messages.append(safe_response_message)
                        
                        for tool_call in tool_calls:
                            func_name = tool_call.function.name
                            print(f"{C.YELLOW}⚡ Fallback Tool Call: {func_name}{C.RESET}")
                            await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": f"[Executing {func_name}...] "}))
                            
                            try:
                                args = json.loads(tool_call.function.arguments)
                            except json.JSONDecodeError:
                                args = {}
                            
                            tool_start = time.time()
                            tool_result = ""
                            
                            if func_name == "get_weather":
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
                            elif func_name == "look_at_screen":
                                tool_result = await analyze_screen(args.get("query", "Describe what is on the screen."))
                            elif func_name == "search_wikipedia":
                                tool_result = search_wikipedia(args.get("query", ""))
                            elif func_name == "search_web":
                                tool_result = search_web(args.get("query", ""))
                            elif func_name == "remember_fact":
                                tool_result = remember_fact(args.get("fact", ""))
                            elif func_name == "recall_memory":
                                tool_result = recall_memory(args.get("query", ""))
                            else:
                                tool_result = "Tool not recognized."
                            
                            tool_ms = int((time.time() - tool_start) * 1000)
                            print(f"{C.GREEN}✓ Fallback Result [{tool_ms}ms]: {tool_result}{C.RESET}")
                            
                            temp_messages.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": func_name,
                                "content": tool_result,
                            })
                        
                        stream_completion = await call_openai_with_rotation(
                            model="gpt-4o-mini",
                            messages=temp_messages,
                            temperature=0.7,
                            max_tokens=150,
                            stream=True
                        )
                    else:
                        stream_completion = await call_openai_with_rotation(
                            model="gpt-4o-mini",
                            messages=temp_messages,
                            temperature=0.7,
                            max_tokens=150,
                            stream=True
                        )
                        
                    llm_response = ""
                    sentence_buffer = ""
                    async for chunk in stream_completion:
                        if not chunk.choices:
                            continue
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
                    
                    if llm_response.strip():
                        print(f"{C.MAGENTA}{C.BOLD}Entropy (Fallback):{C.RESET} {C.MAGENTA}{llm_response}{C.RESET}")
                        conversation_history.append({"role": "user", "content": user_text})
                        conversation_history.append({"role": "assistant", "content": llm_response})
                        if len(conversation_history) > 15:
                            conversation_history[:] = [conversation_history[0]] + conversation_history[-14:]
                except Exception as oe:
                    print(f"{C.RED}✗ OpenAI Fallback failed: {oe}{C.RESET}")
                    await speak_text("My systems are currently experiencing critical API failures.")
            else:
                await speak_text("My systems are currently experiencing critical API failures.")
                
            return
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
                user_text = payload.get("text", "").strip()
                if not user_text:
                    continue
                    
                print(f"{C.CYAN}{C.BOLD}User:{C.RESET} {C.CYAN}{user_text}{C.RESET}")
                
                if current_task and not current_task.done():
                    current_task.cancel()
                    
                current_task = asyncio.create_task(generate_response(user_text))
                
            elif payload.get("type") == "interrupt":
                if current_task and not current_task.done():
                    current_task.cancel()
                    
    except WebSocketDisconnect:
        print(f"{C.DIM}Client disconnected.{C.RESET}")
    except Exception as e:
        print(f"{C.RED}Socket error: {e}{C.RESET}")

if __name__ == "__main__":
    import uvicorn
    
    # ── Startup Banner ──────────────────────────────────────
    print(f"\n{C.CYAN}{C.BOLD}")
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║                                                       ║")
    print("  ║   ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗ ║")
    print("  ║   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝ ║")
    print("  ║   ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗ ║")
    print("  ║   ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║ ║")
    print("  ║   ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║ ║")
    print("  ║   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝ ║")
    print("  ║                        V                                ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print(f"{C.RESET}")
    
    # System Status
    ds_count = len(deepseek_keys)
    gq_count = len(groq_keys)
    oa_count = len(openai_keys)
    gm_count = len(gemini_keys)
    primary = os.getenv("PRIMARY_BRAIN", "deepseek").upper()
    
    print(f"  {C.BOLD}Agent:{C.RESET}    {C.GREEN}Entropy{C.RESET}")
    print(f"  {C.BOLD}Primary:{C.RESET}  {C.GREEN}{primary}{C.RESET}")
    print(f"  {C.BOLD}LLM Keys:{C.RESET} {C.GREEN}DeepSeek({ds_count}){C.RESET} │ {C.GREEN}Groq({gq_count}){C.RESET} │ {C.GREEN}OpenAI({oa_count}){C.RESET}")
    print(f"  {C.BOLD}Vision:{C.RESET}   {C.GREEN}Gemini({gm_count}){C.RESET}")
    print(f"  {C.BOLD}Tools:{C.RESET}    {C.GREEN}{len(tools)} active{C.RESET} (wiki, weather, crypto, calc, news, stocks, webcam, screen, memory×2)")
    print(f"  {C.BOLD}Memory:{C.RESET}   {C.GREEN}{MEMORY_FILE}{C.RESET}")
    print(f"  {C.BOLD}TTS:{C.RESET}      {C.GREEN}en-GB-RyanNeural{C.RESET}")
    print(f"\n  {C.DIM}Starting Uvicorn on http://0.0.0.0:8000 ...{C.RESET}\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
