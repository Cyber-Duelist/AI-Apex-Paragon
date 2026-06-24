"""
SentinelAlpha — LLM Analysis Engine
Groq-powered intelligence pipelines for SEC filings and earnings calls.
"""

import json
import re
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SEC_ANALYSIS_PROMPT, EARNINGS_ANALYSIS_PROMPT, CONVICTION_PROMPT


def _get_client() -> Groq | None:
    """Initialize and return the Groq client."""
    if not GROQ_API_KEY:
        return None
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
        return _get_demo_sec_analysis()
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SEC_ANALYSIS_PROMPT},
                {"role": "user", "content": f"Analyze this SEC filing excerpt:\n\n{filing_text[:12000]}"}
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        print(f"[LLM Engine] SEC analysis error: {e}")
        return _get_demo_sec_analysis()


def analyze_earnings_call(transcript: str) -> dict:
    """
    Analyze earnings call transcript using Groq LLM.
    Returns management sentiment, hedge word analysis, forward guidance, and analyst tension.
    """
    client = _get_client()
    if not client:
        return _get_demo_earnings_analysis()
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": EARNINGS_ANALYSIS_PROMPT},
                {"role": "user", "content": f"Analyze this earnings call transcript:\n\n{transcript[:12000]}"}
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        print(f"[LLM Engine] Earnings analysis error: {e}")
        return _get_demo_earnings_analysis()


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
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": CONVICTION_PROMPT},
                {"role": "user", "content": combined_context}
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        return _parse_json_response(response.choices[0].message.content)
    except Exception as e:
        print(f"[LLM Engine] Conviction error: {e}")
        return _get_demo_conviction()


# ─── DEMO / FALLBACK DATA ───────────────────────────────────────────────────
# Used when Groq API key is not set or API fails

def _get_demo_sec_analysis() -> dict:
    return {
        "risk_factors": [
            {"risk": "Dependence on consumer discretionary spending in uncertain macro environment", "severity": "HIGH", "category": "Market"},
            {"risk": "Ongoing antitrust investigations in EU and US markets", "severity": "HIGH", "category": "Regulatory"},
            {"risk": "Supply chain concentration risk in semiconductor sourcing", "severity": "MEDIUM", "category": "Operational"},
            {"risk": "Foreign currency exchange rate exposure across 40+ markets", "severity": "MEDIUM", "category": "Financial"},
            {"risk": "Cybersecurity threats to customer data and intellectual property", "severity": "MEDIUM", "category": "Cybersecurity"},
        ],
        "revenue_guidance": {
            "direction": "POSITIVE",
            "summary": "Management projects mid-single-digit revenue growth driven by AI/cloud segment expansion.",
            "confidence": 0.72
        },
        "litigation_warnings": [
            {"case": "Patent infringement lawsuit pending in District of Delaware", "severity": "MEDIUM"},
            {"case": "EU Digital Markets Act compliance investigation", "severity": "HIGH"},
        ],
        "red_flags": ["Increase in stock-based compensation dilution", "Change in revenue recognition methodology noted in footnotes"],
        "key_metrics_mentioned": ["$42.3B quarterly revenue", "32.1% gross margin", "$18.7B operating cash flow"],
        "overall_sentiment": "NEUTRAL",
        "sentiment_score": 0.15,
        "executive_summary": "Filing reveals a company navigating regulatory headwinds while maintaining solid financial performance. AI-driven segments show strong momentum, but antitrust risks and SBC dilution warrant close monitoring."
    }


def _get_demo_earnings_analysis() -> dict:
    return {
        "management_sentiment": {
            "score": 0.35,
            "label": "CAUTIOUS",
            "reasoning": "CEO used cautiously optimistic language while CFO provided detailed metrics, suggesting measured confidence with awareness of macro risks."
        },
        "hedge_words": {
            "count": 14,
            "density_label": "MEDIUM",
            "examples": ["we believe", "approximately", "cautiously optimistic", "macro environment", "going forward", "challenges"]
        },
        "forward_guidance": {
            "specificity": "MODERATE",
            "key_projections": [
                "Revenue expected in range of $43-45B next quarter",
                "Capex projected at $12B for AI infrastructure buildout",
                "Targeting 200bps margin expansion by fiscal year end"
            ],
            "confidence_level": 0.65
        },
        "analyst_tension": {
            "score": 0.45,
            "hot_topics": ["AI monetization timeline", "China market exposure", "Capital allocation vs buybacks"]
        },
        "key_quotes": [
            "We are in the early innings of the AI transformation and our infrastructure investments will position us for sustained long-term growth.",
            "The macro environment remains fluid, but our diversified revenue streams provide resilience.",
            "We expect to see meaningful margin expansion as our AI workloads scale."
        ],
        "overall_signal": "BUY",
        "executive_summary": "Management is cautiously bullish on AI-driven growth while acknowledging macro uncertainties. Forward guidance is moderately specific with a clear focus on AI capex. Analyst pushback centers on monetization timelines."
    }


def _get_demo_conviction() -> dict:
    return {
        "conviction_score": 38,
        "conviction_label": "BUY",
        "bull_case": "AI infrastructure investments are creating a durable competitive moat. Revenue growth in cloud/AI segments is accelerating and should drive meaningful margin expansion within 2-3 quarters.",
        "bear_case": "Regulatory headwinds from EU antitrust probes could result in structural remedies. High capex burn rate for AI infrastructure may compress free cash flow in the near term.",
        "key_catalyst": "Q3 earnings report expected to show first inflection in AI revenue monetization.",
        "primary_risk": "EU Digital Markets Act enforcement action could force business model changes in key markets.",
        "recommendation": "Initiate a moderate long position with a 12-month horizon. The AI infrastructure buildout creates asymmetric upside if monetization timelines compress. Set a stop-loss at -12% and reassess after Q3 earnings."
    }
