# Synapse V: Omni-Modal AI Assistant

Synapse V is an enterprise-grade, ultra-low-latency Omni-Modal AI application featuring a sophisticated intelligent agent named **Entropy**. It is capable of real-time vision, autonomous tool calling, bidirectional conversational streaming, and features a bulletproof **Cross-Provider Cascading Fallback** architecture designed for maximum uptime.

## 🌟 Core Architecture: The Cascading Engine

The most powerful engineering feature of Synapse V is its custom-built, resilient LLM routing engine. To combat aggressive API rate limits and `402 Insufficient Balance` errors on free tiers, the backend implements a dual-layer survival mechanism:

1. **Intra-Provider Key Rotation**: The engine dynamically loads up to 9 API keys per provider. If a key hits a rate limit or runs out of credits, the system instantly catches the error and rotates to a fresh key on the fly without dropping the user's WebSocket connection.
2. **Cross-Provider Cascading Fallback**: If a provider is completely exhausted (e.g., all 4 DeepSeek keys fail), the system seamlessly pivots to a secondary provider. 
   - **Primary**: DeepSeek (`deepseek-chat`)
   - **Fallback 1**: Groq (`llama-3.1-8b-instant`)
   - **Fallback 2**: OpenAI (`gpt-4o-mini`)
   
*(Providers can be hot-swapped dynamically via the `PRIMARY_BRAIN` environment variable).*

## 🧠 Omni-Modal Capabilities

- **Vision (On-Demand)**: Powered by `gemini-flash-lite-latest`. Entropy can physically "see" the user's environment through the webcam when explicitly asked to look (preventing background API drain).
- **Voice (Bidirectional Streaming)**: 
  - **TTS**: Low-latency synthetic speech generation via `edge-tts` piped directly into the WebSocket for sub-second audio playback.
  - **STT**: Continuous client-side speech recognition.
- **Interruption Handling (Barge-in)**: Detects user interruption locally and halts AI generation streams instantly for natural conversation flow.

## 🛠️ Autonomous Tool Calling
When asked a question requiring external or real-time context, Entropy automatically halts, selects the appropriate tool, retrieves the data, and synthesizes it naturally into conversation:
- **Webcam Sight**: Triggers the Gemini Vision model to analyze the local environment.
- **Wikipedia Search**: Scrapes the Wikipedia API for real-time factual data.
- **Weather Fetcher**: Retrieves live weather data for any global city.
- **Crypto Tracker**: Fetches live Binance ticker prices for cryptocurrencies.

## 🚀 Tech Stack
- **Backend Orchestration**: FastAPI (Async HTTP & WebSockets)
- **Primary LLM**: DeepSeek API (`deepseek-chat`)
- **Fallback LLM**: Groq API (`llama-3.1-8b-instant`)
- **Vision Engine**: Google Gemini API
- **Speech Synthesis**: Edge-TTS
- **Frontend**: Vanilla JS, WebGL Boids Background, Glassmorphic UI

## 💻 Run Locally (For Portfolio Reviewers)

To test Synapse V on your own machine:

1. Clone the repository and install dependencies:
```bash
python -m venv venv
source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux
pip install -r requirements.txt
```

2. Configure your API Keys by creating a `.env` file at the root:
```env
# Define your primary brain (deepseek or groq)
PRIMARY_BRAIN="deepseek"

# Add your API keys (you can add multiple keys by appending numbers: DEEPSEEK1, DEEPSEEK2, etc.)
DEEPSEEK1=your_deepseek_key_here
GROQ_API_KEY_1=your_groq_key_here
GEMINI_API_KEY_1=your_gemini_key_here
```

3. Launch the FastAPI server:
```bash
python main.py
```
Open `http://localhost:8000` in your browser, allow microphone and camera permissions, and say "Hello Entropy!"
