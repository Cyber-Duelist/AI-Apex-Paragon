import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";

export const maxDuration = 60; // Allow up to 60 seconds for Vercel Hobby tier

// Fix Vercel environment variable concatenation bug aggressively
const rawKey = process.env.GROQ_API_KEY || "";
const match = rawKey.match(/gsk_[a-zA-Z0-9]+/);
const cleanKey = match ? match[0] : rawKey;
const groq = new Groq({ apiKey: cleanKey });

const CLARA_SYSTEM_PROMPT = `You are CLARA (Clinical Language & Adaptive Routing Assistant), an intelligent AI triage receptionist for an NHS GP surgery in the UK.

Your role:
1. Greet the patient warmly and professionally.
2. Ask for their name and date of birth.
3. Ask what brings them in today — their main complaint.
4. Ask targeted follow-up questions (duration, severity 1-10, associated symptoms, any red flags).
5. If they describe a VISUAL symptom (rash, skin lesion, mole, swelling, wound, eye problem, etc.) or if they agree to share a photo, you MUST include the exact phrase "[REQUEST_IMAGE]" anywhere in your response. For example: "I can help you better if you share a photo. Please use the buttons below to upload an image. [REQUEST_IMAGE]"
6. Once you have enough information (usually 3-4 exchanges), produce a structured JSON triage block wrapped in <TRIAGE> tags like this:

<TRIAGE>
{
  "patient_name": "John Smith",
  "dob": "01/01/1980",
  "complaint": "Chest tightness for 2 days",
  "duration": "2 days",
  "severity": 7,
  "urgency": "URGENT",
  "action": "Duty Doctor Callback within 2 hours",
  "pharmacy_first": false,
  "red_flags": ["chest pain", "shortness of breath"],
  "clinical_summary": "Patient reports 2-day history of chest tightness, rated 7/10. Denies radiation. SOB on exertion. No fever. No trauma. Requires same-day clinical review.",
  "needs_image": false
}
</TRIAGE>

Urgency levels: EMERGENCY (call 999 immediately), URGENT (same-day), ROUTINE (within 2 weeks), ADMIN (non-clinical).
Pharmacy First conditions: sore throat, sinusitis, earache, infected insect bite, impetigo, shingles, uncomplicated UTI in women.
Always be empathetic, clear, and reassuring. Never diagnose. You are routing and summarising only.
Keep responses concise and conversational. One or two questions at a time maximum.`;

export async function POST(req: NextRequest) {
  try {
    const { messages, sessionId } = await req.json();

    const FALLBACK_MODELS = [
      "llama-3.1-8b-instant",
      "llama-3.3-70b-versatile",
      "mixtral-8x7b-32768",
      "gemma2-9b-it"
    ];

    let completion = null;
    let lastError = null;

    for (const model of FALLBACK_MODELS) {
      try {
        completion = await groq.chat.completions.create({
          model,
          messages: [
            { role: "system", content: CLARA_SYSTEM_PROMPT },
            ...messages,
          ],
          temperature: 0.4,
          max_tokens: 800,
          stream: false,
        });
        break; // Success
      } catch (err: any) {
        console.warn(`Model ${model} failed:`, err.message);
        lastError = err;
      }
    }

    if (!completion) {
      throw new Error(`All Groq models failed. Last error: ${lastError?.message}`);
    }

    const content = completion.choices[0].message.content || "";

    // Extract triage data if present
    let triageData = null;
    const triageMatch = content.match(/<TRIAGE>([\s\S]*?)<\/TRIAGE>/);
    if (triageMatch) {
      try {
        triageData = JSON.parse(triageMatch[1].trim());
      } catch {
        triageData = null;
      }
    }

    // Check if CLARA is requesting an image using the robust token
    const needsImage = content.includes("[REQUEST_IMAGE]");

    const cleanContent = content
      .replace(/<TRIAGE>[\s\S]*?<\/TRIAGE>/, "")
      .replace(/\[REQUEST_IMAGE\]/g, "")
      .trim();

    return NextResponse.json({
      message: cleanContent,
      triageData,
      needsImage,
      sessionId,
    });
  } catch (error: any) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: error.message || String(error) },
      { status: 500 }
    );
  }
}
