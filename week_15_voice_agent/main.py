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

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Omni-Modal Voice Agent API")
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

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
        
        if latest_frame_base64:
            model_name = "llama-3.2-11b-vision-preview"
            msg_content = [
                {"type": "text", "text": f"Look at my webcam frame: {user_text}"},
                {"type": "image_url", "image_url": {"url": latest_frame_base64}}
            ]
            print("Using Vision Model")
        else:
            model_name = "llama-3.1-8b-instant"
            msg_content = user_text
            print("Using Standard Agent Model")
            
        temp_messages = conversation_history + [{"role": "user", "content": msg_content}]
        
        try:
            completion = await groq_client.chat.completions.create(
                model=model_name,
                messages=temp_messages,
                temperature=0.7,
                max_tokens=200,
                tools=tools if not latest_frame_base64 else None,
                tool_choice="auto" if not latest_frame_base64 else "none"
            )
            
            response_message = completion.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                print(f"Agent requested tool: {tool_calls[0].function.name}")
                await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": "[Searching Web...] "}))
                
                if tool_calls[0].function.name == "search_wikipedia":
                    args = json.loads(tool_calls[0].function.arguments)
                    search_result = search_wikipedia(args.get("query"))
                    print(f"Tool Result: {search_result}")
                    
                    temp_messages.append(response_message)
                    temp_messages.append({
                        "tool_call_id": tool_calls[0].id,
                        "role": "tool",
                        "name": "search_wikipedia",
                        "content": search_result,
                    })
                    
                    stream_completion = await groq_client.chat.completions.create(
                        model=model_name,
                        messages=temp_messages,
                        temperature=0.7,
                        max_tokens=150,
                        stream=True
                    )
                else:
                    stream_completion = None
            else:
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
