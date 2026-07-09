# Synapse V: Omni-Modal Agent

An enterprise-grade, ultra-low-latency Omni-Modal AI capable of real-time vision, autonomous tool calling, and bidirectional conversational streaming. 

## System Architecture

The architecture relies on a persistent WebSocket connection from the client, bridging to an asynchronous backend orchestration pipeline:

1. **Live Webcam Vision:** The browser silently captures a base64 JPEG from the webcam every 3 seconds and streams it over the WebSocket.
2. **Dynamic LLM Routing:** 
   - If an image is detected in the payload, the backend routes the query to **Groq's `llama-3.2-11b-vision-preview`** so the agent can physically "see" the user's environment.
   - If no image is present, it routes to **`llama-3.1-8b-instant`** for maximum speed.
3. **Autonomous Tool Calling:** If the user asks a question the agent doesn't know, it pauses, triggers a Python function to scrape Wikipedia's real-time API, and synthesizes the live data into its answer.
4. **Text-to-Speech (TTS):** Low-latency synthetic speech generation is handled via `edge-tts` directly piped into the WebSocket for sub-second audio playback.

## Features
- **Omni-Modality:** Can see (Webcam), hear (Mic), and speak (TTS) simultaneously.
- **Sub-500ms TTFB:** Heavily optimized asynchronous loops and streaming chunk processors.
- **Interruption Handling (Barge-in):** Detects user interruption locally and halts TTS generation streams instantly.

## Tech Stack
- **FastAPI:** Core async routing and WebSocket management.
- **WebSockets:** Bidirectional audio/video streaming and state syncing.
- **Groq API:** LLaMA-3.2 Vision & LLaMA-3.1 8B Instant.
- **Edge-TTS:** Fast, free synthetic voice generation.

## Run Locally
```bash
python -m venv venv
source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux
pip install -r requirements.txt

# Add your Groq API key to .env at project root
# GROQ_API_KEY=your_key_here

python main.py
```
Open `http://localhost:8000` in your browser.
