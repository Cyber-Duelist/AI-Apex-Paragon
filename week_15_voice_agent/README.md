# Real-Time Voice AI Agent & Workflow Orchestration

An enterprise-grade, ultra-low-latency voice agent capable of bidirectional conversational streaming. Built for deployment in environments requiring sub-500ms Time-To-First-Byte (TTFB).

## System Architecture

The architecture relies on a persistent WebSocket connection from the client, bridging to an asynchronous backend pipeline:
1. **Speech-to-Text (STT):** Real-time streaming transcription via Deepgram/Whisper APIs.
2. **LLM Orchestration:** Streaming inference from LLaMA-3 (via Groq) to minimize latency.
3. **Text-to-Speech (TTS):** Low-latency synthetic speech generation via ElevenLabs.
4. **Server-Sent Events (SSE):** For state updates and transcript broadcasting to the frontend.

## Features
- **Sub-500ms TTFB:** Heavily optimized asynchronous loops and streaming chunk processors.
- **Interruption Handling (Barge-in):** Detects user interruption locally and halts TTS generation streams instantly.
- **Stateful Memory:** Maintains conversation context across multiple turns without inflating prompt size unnecessarily.

## Tech Stack
- **FastAPI:** Core async routing and WebSocket management.
- **WebSockets / SSE:** Bidirectional audio streaming and state syncing.
- **Python `asyncio`:** Concurrent buffer processing.
- **ElevenLabs API:** Premium low-latency synthetic voice generation.

## Run Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
