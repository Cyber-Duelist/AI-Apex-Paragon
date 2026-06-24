"""
SentinelAlpha — Configuration & Constants
Central configuration for SEC EDGAR API, LLM prompts, and scoring parameters.
"""

import os

# ─── SEC EDGAR API ───────────────────────────────────────────────────────────
SEC_BASE_URL = "https://data.sec.gov"
SEC_SEARCH_URL = "https://efts.sec.gov/LATEST"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"
SEC_USER_AGENT = "SentinelAlpha Research adarshsingh@sentinelalpha.ai"

# Popular ticker → CIK mappings (zero-padded to 10 digits)
TICKER_CIK_MAP = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "TSLA": "0001318605",
    "NVDA": "0001045810",
    "META": "0001326801",
    "JPM": "0000019617",
    "V": "0001403161",
    "JNJ": "0000200406",
    "WMT": "0000104169",
    "PG": "0000080424",
    "UNH": "0000731766",
    "MA": "0001141391",
    "HD": "0000354950",
    "DIS": "0001744489",
    "BAC": "0000070858",
    "NFLX": "0001065280",
    "CRM": "0001108524",
    "AMD": "0000002488",
    # Global ADRs
    "INFY": "0001067491", # Infosys (India)
    "HDB": "0001144967",  # HDFC Bank (India)
    "ASML": "0000937966", # ASML (Europe)
    "TSM": "0001046179",  # TSMC (Asia)
    "BABA": "0001577552", # Alibaba (Asia)
    "SONY": "0000313838", # Sony (Asia)
}

# ─── GROQ LLM ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ─── LLM SYSTEM PROMPTS ─────────────────────────────────────────────────────

SEC_ANALYSIS_PROMPT = """You are SentinelAlpha, an elite financial intelligence AI used by hedge fund analysts.
Analyze the following SEC filing excerpt and produce a structured JSON report.

Return ONLY valid JSON with this exact structure:
{
  "risk_factors": [
    {"risk": "Brief description", "severity": "HIGH|MEDIUM|LOW", "category": "Regulatory|Financial|Operational|Legal|Market|Cybersecurity"}
  ],
  "revenue_guidance": {
    "direction": "POSITIVE|NEGATIVE|NEUTRAL",
    "summary": "One-line summary of revenue/earnings outlook",
    "confidence": 0.0-1.0
  },
  "litigation_warnings": [
    {"case": "Brief description", "severity": "HIGH|MEDIUM|LOW"}
  ],
  "red_flags": ["List of accounting or disclosure red flags, if any"],
  "key_metrics_mentioned": ["List of specific financial metrics or figures mentioned"],
  "overall_sentiment": "BULLISH|BEARISH|NEUTRAL",
  "sentiment_score": -1.0 to 1.0,
  "executive_summary": "2-3 sentence summary for a portfolio manager"
}"""

EARNINGS_ANALYSIS_PROMPT = """You are SentinelAlpha, an elite financial intelligence AI used by hedge fund analysts.
Analyze the following earnings call transcript excerpt and produce a structured JSON report.

Focus on detecting management psychology:
- Are they confident or evasive?
- Are they using hedge words ("approximately", "we believe", "challenges")?
- Is their forward guidance concrete (with numbers) or vague?
- Are analysts pushing back or satisfied?

Return ONLY valid JSON with this exact structure:
{
  "management_sentiment": {
    "score": -1.0 to 1.0,
    "label": "CONFIDENT|CAUTIOUS|EVASIVE|DEFENSIVE",
    "reasoning": "Brief explanation"
  },
  "hedge_words": {
    "count": 0,
    "density_label": "LOW|MEDIUM|HIGH|CRITICAL",
    "examples": ["List of hedge phrases found"]
  },
  "forward_guidance": {
    "specificity": "CONCRETE|MODERATE|VAGUE",
    "key_projections": ["List of specific forward-looking statements"],
    "confidence_level": 0.0-1.0
  },
  "analyst_tension": {
    "score": 0.0 to 1.0,
    "hot_topics": ["Topics where analysts pushed back"]
  },
  "key_quotes": ["2-3 most important direct quotes from management"],
  "overall_signal": "STRONG_BUY|BUY|HOLD|SELL|STRONG_SELL",
  "executive_summary": "2-3 sentence summary for a portfolio manager"
}"""

CONVICTION_PROMPT = """You are SentinelAlpha, synthesizing all intelligence into a final conviction score.
Given the SEC filing analysis and earnings call analysis below, produce a final investment conviction.

Return ONLY valid JSON:
{
  "conviction_score": -100 to 100,
  "conviction_label": "STRONG_BUY|BUY|HOLD|SELL|STRONG_SELL",
  "bull_case": "2-sentence bull case",
  "bear_case": "2-sentence bear case",
  "key_catalyst": "The single most important upcoming catalyst",
  "primary_risk": "The single biggest risk",
  "recommendation": "3-sentence actionable recommendation for a portfolio manager"
}"""

# ─── SCORING PARAMETERS ─────────────────────────────────────────────────────

HEDGE_WORDS = [
    "approximately", "we believe", "we expect", "challenges",
    "uncertainties", "may", "might", "could", "potentially",
    "we anticipate", "subject to", "it is possible", "generally",
    "substantially", "relatively", "somewhat", "in our view",
    "we think", "going forward", "headwinds", "tailwinds",
    "cautiously optimistic", "macro environment", "normalizing"
]

CONVICTION_THRESHOLDS = {
    "STRONG_BUY": (60, 100),
    "BUY": (20, 59),
    "HOLD": (-19, 19),
    "SELL": (-59, -20),
    "STRONG_SELL": (-100, -60),
}

CONVICTION_COLORS = {
    "STRONG_BUY": "#00ff88",
    "BUY": "#00cc66",
    "HOLD": "#ffaa00",
    "SELL": "#ff6644",
    "STRONG_SELL": "#ff2233",
}
