# CLARA AI — Clinical Language & Adaptive Routing Assistant

## Overview
CLARA AI is a multimodal AI receptionist designed to automate NHS GP triage. By integrating live text-to-speech, real-time image analysis of wounds using Vision AI, and an auto-updating Clinical Command Center for doctors, CLARA bridges the gap between patient intake and clinical action.

## Key Features
- **Voice AI Pipeline**: Bidirectional real-time speech-to-text (STT) and text-to-speech (TTS) streaming via WebSockets.
- **Vision AI Diagnosis**: Utilizes LLaMA 3.3 Vision AI to analyze uploaded wound images and immediately flag critical conditions to clinicians.
- **Clinical Command Center**: A live updating dashboard where doctors can review patient symptoms, AI-assessed urgency levels, and direct transcripts.
- **Mobile Optimized**: Designed with responsive glassmorphism UI that supports direct camera uploads on mobile devices.

## Architecture
- **Frontend**: Next.js App Router, React Hooks for state management, Vanilla CSS with custom media queries for responsiveness.
- **Backend**: Groq Cloud SDK for ultra-low latency LLM inference.
- **AI Models**: LLaMA 3 70B (Text), LLaMA 3.3 Vision (Image Analysis).

## Impact
- Eliminates manual transcription of patient symptoms.
- Reduces patient waiting times by providing instant triage categorization.
- Enhances remote diagnosis capabilities by allowing patients to securely submit visual evidence of physical symptoms.
