from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
from dotenv import load_dotenv
import edge_tts
from groq import AsyncGroq

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Free Voice Agent API")
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

conversation_history = [
    {"role": "system", "content": "You are Entropy, a helpful, extremely concise, and witty AI assistant. Keep responses under 2 sentences to ensure fast voice generation."}
]

@app.get("/")
async def get_frontend():
    with open(Path(__file__).parent / "index.html", "r") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/stream")
async def websocket_audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to Voice Pipeline")
    
    current_task = None
    
    async def generate_response(user_text):
        conversation_history.append({"role": "user", "content": user_text})
        await websocket.send_text(json.dumps({"type": "clear"}))
        
        llm_response = ""
        sentence_buffer = ""
        
        try:
            completion = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=conversation_history,
                temperature=0.7,
                max_tokens=150,
                stream=True
            )
            
            async for chunk in completion:
                token = chunk.choices[0].delta.content or ""
                llm_response += token
                sentence_buffer += token
                
                if token:
                    await websocket.send_text(json.dumps({"type": "ai_response_chunk", "text": token}))
                    
                # Flush to TTS on sentence boundary to minimize TTFB latency
                if any(p in token for p in ['.', '!', '?', '\n']):
                    text_to_speak = sentence_buffer.strip()
                    if text_to_speak:
                        communicate = edge_tts.Communicate(text_to_speak, "en-US-ChristopherNeural")
                        audio_data = bytearray()
                        async for tts_chunk in communicate.stream():
                            if tts_chunk["type"] == "audio":
                                audio_data.extend(tts_chunk["data"])
                        if audio_data:
                            await websocket.send_bytes(bytes(audio_data))
                    sentence_buffer = ""
                    
            # Flush any remaining buffer at the end of the stream
            if sentence_buffer.strip():
                communicate = edge_tts.Communicate(sentence_buffer.strip(), "en-US-ChristopherNeural")
                audio_data = bytearray()
                async for tts_chunk in communicate.stream():
                    if tts_chunk["type"] == "audio":
                        audio_data.extend(tts_chunk["data"])
                if audio_data:
                    await websocket.send_bytes(bytes(audio_data))
                        
            conversation_history.append({"role": "assistant", "content": llm_response})
            print(f"Entropy: {llm_response}")
            
        except asyncio.CancelledError:
            print("Generation interrupted.")
            if llm_response:
                 conversation_history.append({"role": "assistant", "content": llm_response + "..."})
            raise
        except Exception as e:
            print(f"LLM/TTS Error: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("type") == "user_speech":
                user_text = payload.get("text", "")
                print(f"User: {user_text}")
                
                if current_task and not current_task.done():
                    current_task.cancel()
                    
                current_task = asyncio.create_task(generate_response(user_text))
                
            elif payload.get("type") == "interrupt":
                print("Interrupt received.")
                if current_task and not current_task.done():
                    current_task.cancel()
                    
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"Pipeline error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
