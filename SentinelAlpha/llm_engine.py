"""
SentinelAlpha — LLM Analysis Engine
Groq-powered intelligence pipelines for SEC filings and earnings calls.
"""

import json
import re
import os
import time
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SEC_ANALYSIS_PROMPT, EARNINGS_ANALYSIS_PROMPT, CONVICTION_PROMPT


def is_live_mode() -> bool:
    """Check if the Groq API key is configured."""
    return bool(GROQ_API_KEY)


def _get_client() -> Groq | None:
    """Initialize and return the Groq client."""
    if not GROQ_API_KEY:
        print("[LLM Engine] WARNING: GROQ_API_KEY is not set! Running in DEMO MODE.")
        print(f"[LLM Engine] Environment check - GROQ_API_KEY length: {len(os.getenv('GROQ_API_KEY', ''))}")
        return None
    print(f"[LLM Engine] LIVE MODE - API key detected (length: {len(GROQ_API_KEY)})")
    return Groq(api_key=GROQ_API_KEY)


def _parse_json_response(text: str) -> dict:
    """Robustly extract JSON from an LLM response that may contain markdown fences."""
    # Try to find JSON within markdown code blocks
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to parse the entire response as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find any JSON object in the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    return {"error": "Failed to parse LLM response", "raw": text[:500]}


def analyze_sec_filing(filing_text: str) -> dict:
    """
    Analyze SEC filing text using Groq LLM.
    Returns structured analysis with risk factors, guidance, litigation, and sentiment.
    """
    client = _get_client()
    if not client:
        return _get_demo_sec_analysis(filing_text)
    
    if not filing_text or len(filing_text.strip()) < 100:
        print("[LLM Engine] Filing text too short, using demo data")
        return _get_demo_sec_analysis(filing_text)
    
    try:
        input_text = filing_text[:5000]
        print(f"[LLM Engine] Sending {len(input_text)} chars to Groq for SEC analysis...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SEC_ANALYSIS_PROMPT},
                {"role": "user", "content": f"Analyze this SEC filing excerpt:\n\n{input_text}"}
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        result = _parse_json_response(response.choices[0].message.content)
        result["_source"] = "LIVE_API"
        print(f"[LLM Engine] SEC analysis complete. Sentiment: {result.get('sentiment_score', 'N/A')}")
        return result
    except Exception as e:
        print(f"[LLM Engine] SEC analysis error: {e}")
        demo = _get_demo_sec_analysis(filing_text)
        demo["_error"] = str(e)
        return demo


def analyze_earnings_call(transcript: str) -> dict:
    """
    Analyze earnings call transcript using Groq LLM.
    Returns management sentiment, hedge word analysis, forward guidance, and analyst tension.
    """
    client = _get_client()
    if not client:
        return _get_demo_earnings_analysis(transcript)
    
    if not transcript or len(transcript.strip()) < 100:
        print("[LLM Engine] Transcript text too short, using demo data")
        return _get_demo_earnings_analysis(transcript)
    
    try:
        time.sleep(2)  # Rate limit spacing between API calls
        input_text = transcript[:5000]
        print(f"[LLM Engine] Sending {len(input_text)} chars to Groq for earnings analysis...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": EARNINGS_ANALYSIS_PROMPT},
                {"role": "user", "content": f"Analyze this earnings call transcript:\n\n{input_text}"}
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        result = _parse_json_response(response.choices[0].message.content)
        result["_source"] = "LIVE_API"
        print(f"[LLM Engine] Earnings analysis complete. Signal: {result.get('overall_signal', 'N/A')}")
        return result
    except Exception as e:
        print(f"[LLM Engine] Earnings analysis error: {e}")
        demo = _get_demo_earnings_analysis(transcript)
        demo["_error"] = str(e)
        return demo


def generate_conviction(sec_analysis: dict, earnings_analysis: dict, ticker: str) -> dict:
    """
    Synthesize SEC filing and earnings call analyses into a final conviction score.
    """
    client = _get_client()
    if not client:
        return _get_demo_conviction()
    
    combined_context = f"""
COMPANY: {ticker}

=== SEC FILING ANALYSIS ===
{json.dumps(sec_analysis, indent=2)}

=== EARNINGS CALL ANALYSIS ===
{json.dumps(earnings_analysis, indent=2)}
"""
    
    try:
        time.sleep(2)  # Rate limit spacing between API calls
        print(f"[LLM Engine] Generating conviction for {ticker}...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": CONVICTION_PROMPT},
                {"role": "user", "content": combined_context}
            ],
            temperature=0.2,
            max_tokens=512,
        )
        result = _parse_json_response(response.choices[0].message.content)
        result["_source"] = "LIVE_API"
        print(f"[LLM Engine] Conviction complete: {result.get('conviction_score', 'N/A')} ({result.get('conviction_label', 'N/A')})")
        return result
    except Exception as e:
        print(f"[LLM Engine] Conviction error: {e}")
        demo = _get_demo_conviction()
        demo["_error"] = str(e)
        return demo


# ─── DEMO / FALLBACK DATA ───────────────────────────────────────────────────
# Used when Groq API key is not set or API fails
# These now attempt basic text analysis to produce varied results

def _basic_text_sentiment(text: str) -> tuple:
    """Simple keyword-based sentiment when LLM is unavailable."""
    if not text:
        return 0.0, "NEUTRAL"
    
    text_lower = text.lower()
    
    positive_words = ["growth", "strong", "exceeded", "record", "profit", "increase", 
                      "expansion", "innovation", "improved", "outperformed", "momentum",
                      "robust", "healthy", "milestone", "accelerat"]
    negative_words = ["risk", "loss", "decline", "lawsuit", "litigation", "impairment",
                      "uncertainty", "adverse", "challenging", "headwind", "weakness",
                      "restructuring", "default", "violation", "penalty", "deficit"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0, "NEUTRAL"
    
    score = round((pos_count - neg_count) / max(total, 1) * 0.8, 2)
    score = max(-1.0, min(1.0, score))
    
    if score > 0.2:
        sentiment = "BULLISH"
    elif score < -0.2:
        sentiment = "BEARISH"
    else:
        sentiment = "NEUTRAL"
    
    return score, sentiment


def _extract_risk_keywords(text: str) -> list:
    """Extract basic risk indicators from text."""
    if not text:
        return [
            {"risk": "Unable to parse filing - no text extracted", "severity": "HIGH", "category": "Operational"},
        ]
    
    text_lower = text.lower()
    risks = []
    
    risk_patterns = {
        ("competition", "competitive"): ("Competitive pressures in core markets", "MEDIUM", "Market"),
        ("regulation", "regulatory", "compliance"): ("Regulatory compliance requirements", "MEDIUM", "Regulatory"),
        ("litigation", "lawsuit", "legal proceed"): ("Pending legal proceedings", "HIGH", "Legal"),
        ("cybersecurity", "data breach", "security incident"): ("Cybersecurity and data protection risks", "MEDIUM", "Cybersecurity"),
        ("supply chain", "supplier"): ("Supply chain concentration risk", "MEDIUM", "Operational"),
        ("foreign currency", "exchange rate"): ("Foreign currency exchange exposure", "LOW", "Financial"),
        ("interest rate",): ("Interest rate sensitivity", "MEDIUM", "Financial"),
        ("climate", "environmental"): ("Environmental and climate-related risks", "LOW", "Regulatory"),
        ("acquisition", "integration"): ("Acquisition integration risk", "MEDIUM", "Operational"),
        ("impairment", "goodwill"): ("Asset impairment and goodwill risk", "HIGH", "Financial"),
    }
    
    for keywords, (risk_desc, severity, category) in risk_patterns.items():
        if any(kw in text_lower for kw in keywords):
            risks.append({"risk": risk_desc, "severity": severity, "category": category})
    
    if not risks:
        risks.append({"risk": "Standard business risks disclosed", "severity": "LOW", "category": "Market"})
    
    return risks[:6]


def _get_demo_sec_analysis(filing_text: str = "") -> dict:
    score, sentiment = _basic_text_sentiment(filing_text)
    risks = _extract_risk_keywords(filing_text)
    
    if filing_text and len(filing_text) > 200:
        preview = filing_text[:300].replace("\n", " ").strip()
        summary = f"[DEMO MODE] Basic text analysis of filing. Preview: {preview}..."
    else:
        summary = "[DEMO MODE] No Groq API key configured. Set GROQ_API_KEY in Hugging Face Space secrets for real AI analysis."
    
    return {
        "risk_factors": risks,
        "revenue_guidance": {
            "direction": "POSITIVE" if score > 0 else ("NEGATIVE" if score < 0 else "NEUTRAL"),
            "summary": "Demo mode - set GROQ_API_KEY for real guidance extraction.",
            "confidence": 0.0
        },
        "litigation_warnings": [],
        "red_flags": ["Running in DEMO MODE - results are from basic keyword analysis, not AI"],
        "key_metrics_mentioned": [],
        "overall_sentiment": sentiment,
        "sentiment_score": score,
        "executive_summary": summary,
        "_source": "DEMO_MODE"
    }


def _get_demo_earnings_analysis(transcript: str = "") -> dict:
    score, _ = _basic_text_sentiment(transcript)
    
    if score > 0.2:
        label = "CONFIDENT"
    elif score < -0.2:
        label = "DEFENSIVE"
    else:
        label = "CAUTIOUS"
    
    return {
        "management_sentiment": {
            "score": score,
            "label": label,
            "reasoning": "Demo mode - basic keyword sentiment. Set GROQ_API_KEY for real analysis."
        },
        "hedge_words": {
            "count": 0,
            "density_label": "N/A",
            "examples": ["Demo mode - hedge word detection requires Groq API"]
        },
        "forward_guidance": {
            "specificity": "N/A",
            "key_projections": ["Demo mode - set GROQ_API_KEY for real guidance extraction"],
            "confidence_level": 0.0
        },
        "analyst_tension": {
            "score": 0.0,
            "hot_topics": ["Demo mode"]
        },
        "key_quotes": ["Demo mode - no AI analysis available without GROQ_API_KEY"],
        "overall_signal": "HOLD",
        "executive_summary": "[DEMO MODE] Set GROQ_API_KEY in Hugging Face Space secrets for real earnings analysis.",
        "_source": "DEMO_MODE"
    }


def _get_demo_conviction() -> dict:
    return {
        "conviction_score": 0,
        "conviction_label": "HOLD",
        "bull_case": "Demo mode - real AI bull case analysis requires GROQ_API_KEY.",
        "bear_case": "Demo mode - real AI bear case analysis requires GROQ_API_KEY.",
        "key_catalyst": "Set up GROQ_API_KEY to unlock real catalyst detection.",
        "primary_risk": "No API key configured - all analysis is placeholder data.",
        "recommendation": "DEMO MODE: This is NOT real analysis. Go to Settings > Secrets on your Hugging Face Space and add GROQ_API_KEY to enable live AI-powered intelligence.",
        "_source": "DEMO_MODE"
    }
