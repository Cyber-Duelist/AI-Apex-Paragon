# Case Study: Meeting Intelligence Pipeline

## 🔴 The Problem
Corporate meetings produce massive amounts of unstructured audio data. Employees waste hours listening to recordings to extract action items, decisions, and summaries. Traditional transcription services only provide raw text, which still requires human effort to synthesize into useful business intelligence.

## 🟢 The Solution
We built an end-to-end **Meeting Intelligence Pipeline** (Week 13) that ingests raw audio/video files and transforms them into structured, actionable business reports.

The pipeline uses state-of-the-art speech-to-text models (Whisper) to generate an accurate transcript. That transcript is then fed into an advanced LLM which extracts the core summary, key decisions made, and specifically assigns action items to individual team members. We wrapped this in a modern, dark-themed Web UI for easy employee access.

## 🛠️ Architecture & Technologies
- **Backend:** `FastAPI`, `Python`
- **Frontend:** `HTML/CSS`, Vanilla `JavaScript`
- **Audio Processing:** `OpenAI Whisper API` (Speech-to-Text)
- **NLP Extraction:** `Groq API`, `LLaMA 3`

## 📈 Business Value
1. **Automated Documentation:** Eliminates the need for a human note-taker during meetings.
2. **Accountability:** Automatically extracts and highlights action items so critical tasks are not forgotten.
3. **Time Efficiency:** Allows executives and absentees to consume a 60-minute meeting in a 2-minute structured read.
