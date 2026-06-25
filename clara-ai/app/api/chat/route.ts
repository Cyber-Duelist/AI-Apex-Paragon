import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";

export const maxDuration = 60; // Allow up to 60 seconds for Vercel Hobby tier

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

const CLARA_SYSTEM_PROMPT = `You are CLARA (Clinical Language & Adaptive Routing Assistant), an intelligent AI triage receptionist for an NHS GP surgery in the UK.

Your role:
1. Greet the patient warmly and professionally.
2. Ask for their name and date of birth.
3. Ask what brings them in today — their main complaint.
4. Ask targeted follow-up questions (duration, severity 1-10, associated symptoms, any red flags).
5. If they describe a VISUAL symptom (rash, skin lesion, mole, swelling, wound, eye problem, etc.), tell them: "I can help you better if you share a photo. Please tap the camera icon below to upload an image."
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

    // Check if CLARA is requesting an image
    const needsImage =
      content.toLowerCase().includes("share a photo") ||
      content.toLowerCase().includes("upload an image") ||
      content.toLowerCase().includes("camera icon");

    const cleanContent = content.replace(/<TRIAGE>[\s\S]*?<\/TRIAGE>/, "").trim();

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
