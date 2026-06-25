import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";

export const maxDuration = 60; // Allow up to 60 seconds for Vercel Hobby tier

// Fix Vercel environment variable concatenation bug aggressively
const rawKey = process.env.GROQ_API_KEY || "";
const match = rawKey.match(/gsk_[a-zA-Z0-9]+/);
const cleanKey = match ? match[0] : rawKey;
const groq = new Groq({ apiKey: cleanKey });

const VISION_PROMPT = `You are a clinical AI assistant helping to pre-screen patient-submitted images for an NHS GP surgery. 
Analyze this image and provide a structured clinical assessment.

You MUST respond ONLY with a JSON object in this exact format:
{
  "finding": "describe what the image shows (e.g., skin rash, wound, eye redness)",
  "clinical_observations": ["observation 1", "observation 2", "observation 3"],
  "risk_indicators": ["any concerning features found, or 'none identified'"],
  "urgency_signal": "LOW | MODERATE | HIGH",
  "estimated_severity_out_of_10": "number from 1-10",
  "recommended_action": "brief recommendation for the GP",
  "disclaimer": "AI pre-screening only. Clinical assessment required by a qualified practitioner."
}

Be objective and clinical. Do not diagnose. Use UK clinical terminology where appropriate.`;

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("image") as File;

    if (!file) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const base64 = Buffer.from(bytes).toString("base64");
    const mimeType = file.type || "image/jpeg";

    const response = await groq.chat.completions.create({
      model: "meta-llama/llama-4-scout-17b-16e-instruct",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "image_url",
              image_url: { url: `data:${mimeType};base64,${base64}` },
            },
            { type: "text", text: VISION_PROMPT },
          ],
        },
      ],
      temperature: 0.1,
      max_tokens: 600,
    });

    const raw = response.choices[0].message.content || "";
    const jsonMatch = raw.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("Could not parse vision response");
    }
    const analysis = JSON.parse(jsonMatch[0]);

    return NextResponse.json({ analysis });
  } catch (error) {
    console.error("Vision API error:", error);
    return NextResponse.json(
      { error: "Image analysis failed. Please try again." },
      { status: 500 }
    );
  }
}
