"""
SentinelAlpha — AI Hedge Fund Intelligence Platform
Main Streamlit application with multi-tab dashboard.
"""

import streamlit as st
import json
import time

from sec_client import get_recent_filings, get_filing_document, extract_risk_factors, extract_mda, get_company_name
from llm_engine import analyze_sec_filing, analyze_earnings_call, generate_conviction
from scoring import (
    build_conviction_gauge, build_risk_radar, build_sentiment_bar,
    build_hedge_word_chart, count_hedge_words
)
from config import TICKER_CIK_MAP, CONVICTION_COLORS

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelAlpha | AI Hedge Fund Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
        color: #e0e0e0;
    }
    
    /* Header */
    .sentinel-header {
        text-align: center;
        padding: 2rem 0 1rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.15);
        margin-bottom: 2rem;
    }
    .sentinel-header h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #00e5ff, #ff3366);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        letter-spacing: 3px;
    }
    .sentinel-header p {
        color: #888;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255,255,255, 0.03);
        border: 1px solid rgba(255,255,255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(0, 229, 255, 0.3);
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.05);
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        color: #888;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    
    /* Risk Badge */
    .risk-high { color: #ff3366; border-left: 3px solid #ff3366; padding-left: 8px; }
    .risk-medium { color: #ffaa00; border-left: 3px solid #ffaa00; padding-left: 8px; }
    .risk-low { color: #00cc66; border-left: 3px solid #00cc66; padding-left: 8px; }
    
    /* Quote Block */
    .key-quote {
        border-left: 3px solid #00e5ff;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        background: rgba(0, 229, 255, 0.04);
        font-style: italic;
        color: #ccc;
        border-radius: 0 8px 8px 0;
    }
    
    /* Signal Badge */
    .signal-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 50px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }
    
    /* Section Labels */
    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #00e5ff;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.3rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(10, 15, 25, 0.95);
        border-right: 1px solid rgba(0, 229, 255, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sentinel-header">
    <h1>🛡️ SENTINELALPHA</h1>
    <p>AI-Powered Hedge Fund Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Target Selection")
    
    ticker = st.text_input(
        "Stock Ticker",
        value="NVDA",
        max_chars=6,
        help="Enter a US stock or Global ADR ticker (e.g., AAPL, NVDA, ASML, INFY)"
    ).upper().strip()
    
    filing_type = st.selectbox(
        "Filing Type",
        ["Annual Report (10-K / 20-F)", "Quarterly Report (10-Q / 6-K)"],
        help="Select the SEC filing type to analyze"
    )
    form_type = ["10-K", "20-F"] if "Annual" in filing_type else ["10-Q", "6-K"]
    
    st.markdown("---")
    st.markdown("### 📊 Quick Tickers")
    quick_tickers = ["NVDA", "AAPL", "MSFT", "ASML", "TSLA", "INFY", "BABA", "JPM"]
    cols = st.columns(4)
    for i, t in enumerate(quick_tickers):
        with cols[i % 4]:
            if st.button(t, key=f"qt_{t}", use_container_width=True):
                st.session_state["quick_ticker"] = t
                st.rerun()
    
    # Handle quick ticker selection
    if "quick_ticker" in st.session_state:
        ticker = st.session_state.pop("quick_ticker")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "SentinelAlpha analyzes SEC filings and earnings calls "
        "using LLM-powered intelligence pipelines to generate "
        "actionable alpha conviction scores."
    )
    st.caption("Built by **Adarsh Kumar Singh**")
    st.markdown("[Portfolio](https://cyber-duelist.github.io/AI-Apex-Paragon/) · [GitHub](https://github.com/Cyber-Duelist/AI-Apex-Paragon)")

# ─── MAIN ANALYSIS ───────────────────────────────────────────────────────────
run_analysis = st.button("🚀 Run Full Intelligence Scan", type="primary", use_container_width=True)

if run_analysis and ticker:
    # ── Phase 1: Fetch SEC Data ──────────────────────────────────────────
    with st.status("🔍 Running intelligence scan...", expanded=True) as status:
        st.write(f"Resolving ticker **{ticker}**...")
        company_name = get_company_name(ticker)
        st.write(f"Company: **{company_name}**")
        
        st.write(f"Fetching recent {form_type} filings from SEC EDGAR...")
        filings = get_recent_filings(ticker, form_type=form_type, count=3)
        
        filing_text = ""
        risk_text = ""
        mda_text = ""
        
        if filings:
            latest = filings[0]
            st.write(f"Found filing: **{latest['form']}** ({latest['filingDate']})")
            st.write("Downloading filing document...")
            filing_text = get_filing_document(latest)
            
            if filing_text:
                st.write("Extracting Risk Factors section...")
                risk_text = extract_risk_factors(filing_text)
                st.write("Extracting MD&A section...")
                mda_text = extract_mda(filing_text)
                st.write(f"Extracted **{len(risk_text):,}** chars of risk factors, **{len(mda_text):,}** chars of MD&A")
            else:
                st.warning("Could not download filing document. Using demo analysis.")
        else:
            st.warning(f"No {form_type} filings found for {ticker}. Using demo analysis.")
        
        # ── Phase 2: LLM Analysis ───────────────────────────────────────
        st.write("🧠 Running SEC Filing AI analysis...")
        analysis_text = risk_text if risk_text else filing_text
        sec_analysis = analyze_sec_filing(analysis_text) if analysis_text else analyze_sec_filing("")
        
        st.write("🎙️ Running Earnings Call AI analysis...")
        earnings_text = mda_text if mda_text else ""
        earnings_analysis = analyze_earnings_call(earnings_text) if earnings_text else analyze_earnings_call("")
        
        st.write("📊 Generating Alpha Conviction Score...")
        conviction = generate_conviction(sec_analysis, earnings_analysis, ticker)
        
        status.update(label="✅ Intelligence scan complete!", state="complete")
    
    # Store results in session state
    st.session_state["results"] = {
        "ticker": ticker,
        "company_name": company_name,
        "sec_analysis": sec_analysis,
        "earnings_analysis": earnings_analysis,
        "conviction": conviction,
        "filing_date": filings[0]["filingDate"] if filings else "N/A",
    }

# ─── DISPLAY RESULTS ────────────────────────────────────────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]
    sec = r["sec_analysis"]
    earn = r["earnings_analysis"]
    conv = r["conviction"]
    
    # Company header
    st.markdown(f"## {r['company_name']} ({r['ticker']})")
    st.caption(f"Latest filing date: {r['filing_date']}")
    
    # ── Top Metrics Row ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    
    conv_score = conv.get("conviction_score", 0)
    conv_label = conv.get("conviction_label", "HOLD")
    conv_color = CONVICTION_COLORS.get(conv_label, "#fff")
    
    sec_sentiment = sec.get("sentiment_score", 0)
    earn_sentiment = earn.get("management_sentiment", {}).get("score", 0)
    earn_label = earn.get("management_sentiment", {}).get("label", "N/A")
    
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{conv_color}">{conv_score:+d}</div>
            <div class="metric-label">Conviction Score</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{conv_color}">{conv_label}</div>
            <div class="metric-label">Signal</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        sec_color = "#00cc66" if sec_sentiment >= 0 else "#ff3366"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{sec_color}">{sec_sentiment:+.2f}</div>
            <div class="metric-label">SEC Sentiment</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        earn_color = "#00cc66" if earn_sentiment >= 0 else "#ff3366"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{earn_color}">{earn_label}</div>
            <div class="metric-label">Mgmt Sentiment</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Tabbed Analysis ──────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📄 SEC Filing Intelligence", "🎙️ Earnings Call Analyzer", "📊 Alpha Conviction"])
    
    # ────────────────────────────────────────────────────────────────────
    # TAB 1: SEC FILING INTELLIGENCE
    # ────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-label">Executive Summary</div>', unsafe_allow_html=True)
        st.info(sec.get("executive_summary", "Analysis not available."))
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("#### ⚠️ Risk Factors")
            risk_factors = sec.get("risk_factors", [])
            for rf in risk_factors:
                sev = rf.get("severity", "LOW")
                css_class = f"risk-{sev.lower()}"
                st.markdown(
                    f'<div class="{css_class}"><strong>[{sev}]</strong> '
                    f'<em>{rf.get("category", "")}</em> — {rf.get("risk", "")}</div>',
                    unsafe_allow_html=True
                )
                st.markdown("")
            
            st.markdown("#### 🚩 Red Flags")
            red_flags = sec.get("red_flags", [])
            if red_flags:
                for flag in red_flags:
                    st.markdown(f"- 🔴 {flag}")
            else:
                st.success("No red flags detected.")
        
        with col_right:
            st.markdown("#### 🎯 Risk Radar")
            st.plotly_chart(build_risk_radar(risk_factors), use_container_width=True)
            
            st.markdown("#### 💰 Revenue Guidance")
            guidance = sec.get("revenue_guidance", {})
            direction = guidance.get("direction", "NEUTRAL")
            dir_emoji = {"POSITIVE": "📈", "NEGATIVE": "📉", "NEUTRAL": "➡️"}.get(direction, "➡️")
            st.markdown(f"**{dir_emoji} {direction}** (Confidence: {guidance.get('confidence', 0):.0%})")
            st.caption(guidance.get("summary", ""))
        
        # Litigation
        litigation = sec.get("litigation_warnings", [])
        if litigation:
            st.markdown("#### ⚖️ Litigation & Regulatory")
            for lit in litigation:
                sev = lit.get("severity", "LOW")
                css_class = f"risk-{sev.lower()}"
                st.markdown(f'<div class="{css_class}">⚖️ {lit.get("case", "")}</div>', unsafe_allow_html=True)
        
        # Key Metrics
        metrics = sec.get("key_metrics_mentioned", [])
        if metrics:
            st.markdown("#### 📊 Key Metrics Mentioned")
            metric_cols = st.columns(min(len(metrics), 4))
            for i, m in enumerate(metrics):
                with metric_cols[i % len(metric_cols)]:
                    st.code(m)
    
    # ────────────────────────────────────────────────────────────────────
    # TAB 2: EARNINGS CALL ANALYZER
    # ────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-label">Executive Summary</div>', unsafe_allow_html=True)
        st.info(earn.get("executive_summary", "Analysis not available."))
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("#### 🧠 Management Sentiment")
            mgmt = earn.get("management_sentiment", {})
            sent_score = mgmt.get("score", 0)
            sent_label = mgmt.get("label", "N/A")
            sent_color = "#00cc66" if sent_score > 0.2 else ("#ff3366" if sent_score < -0.2 else "#ffaa00")
            
            st.markdown(
                f'<div class="metric-card"><div class="metric-value" style="color:{sent_color}">'
                f'{sent_label} ({sent_score:+.2f})</div>'
                f'<div class="metric-label">Management Tone</div></div>',
                unsafe_allow_html=True
            )
            st.caption(mgmt.get("reasoning", ""))
            
            st.markdown("#### 📢 Forward Guidance")
            guidance = earn.get("forward_guidance", {})
            spec = guidance.get("specificity", "N/A")
            spec_emoji = {"CONCRETE": "🎯", "MODERATE": "📋", "VAGUE": "🌫️"}.get(spec, "📋")
            st.markdown(f"**Specificity:** {spec_emoji} {spec} (Confidence: {guidance.get('confidence_level', 0):.0%})")
            
            projections = guidance.get("key_projections", [])
            for p in projections:
                st.markdown(f"- 📌 {p}")
        
        with col_right:
            st.markdown("#### 🔤 Hedge Word Analysis")
            hedge = earn.get("hedge_words", {})
            st.plotly_chart(build_hedge_word_chart(hedge), use_container_width=True)
            
            examples = hedge.get("examples", [])
            if examples:
                st.caption("Detected: " + ", ".join(f'`{w}`' for w in examples[:8]))
        
        # Analyst Tension
        tension = earn.get("analyst_tension", {})
        if tension:
            st.markdown("#### 🔥 Analyst Q&A Tension")
            t_score = tension.get("score", 0)
            t_color = "#ff3366" if t_score > 0.6 else ("#ffaa00" if t_score > 0.3 else "#00cc66")
            st.progress(min(t_score, 1.0))
            st.caption(f"Tension Score: **{t_score:.2f}** — Hot Topics: {', '.join(tension.get('hot_topics', []))}")
        
        # Key Quotes
        quotes = earn.get("key_quotes", [])
        if quotes:
            st.markdown("#### 💬 Key Management Quotes")
            for q in quotes:
                st.markdown(f'<div class="key-quote">"{q}"</div>', unsafe_allow_html=True)
    
    # ────────────────────────────────────────────────────────────────────
    # TAB 3: ALPHA CONVICTION
    # ────────────────────────────────────────────────────────────────────
    with tab3:
        col_gauge, col_bars = st.columns([1, 1])
        
        with col_gauge:
            st.markdown("#### 🎯 Conviction Gauge")
            st.plotly_chart(
                build_conviction_gauge(conv_score, conv_label),
                use_container_width=True
            )
        
        with col_bars:
            st.markdown("#### 📊 Signal Comparison")
            st.plotly_chart(
                build_sentiment_bar(sec_sentiment, earn_sentiment, conv_score),
                use_container_width=True
            )
        
        st.markdown("---")
        
        col_bull, col_bear = st.columns(2)
        with col_bull:
            st.markdown("#### 📈 Bull Case")
            st.success(conv.get("bull_case", "N/A"))
            st.markdown("**Key Catalyst**")
            st.info(conv.get("key_catalyst", "N/A"))
        
        with col_bear:
            st.markdown("#### 📉 Bear Case")
            st.error(conv.get("bear_case", "N/A"))
            st.markdown("**Primary Risk**")
            st.warning(conv.get("primary_risk", "N/A"))
        
        st.markdown("---")
        st.markdown("#### 📋 Recommendation")
        st.markdown(f"""
        <div style="background: rgba(0,229,255,0.05); border: 1px solid rgba(0,229,255,0.2); 
                    border-radius: 12px; padding: 1.5rem; font-size: 1.1rem; line-height: 1.6;">
            {conv.get("recommendation", "Run the analysis to generate a recommendation.")}
        </div>
        """, unsafe_allow_html=True)

else:
    # ── Landing State ────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align: center; padding: 3rem; opacity: 0.7;">
        <p style="font-size: 3rem;">🛡️</p>
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: #888;">
            Enter a stock ticker and click <strong>Run Full Intelligence Scan</strong> to begin.
        </p>
        <p style="color: #555; font-size: 0.85rem;">
            SentinelAlpha will fetch the latest SEC filing, analyze risk factors, evaluate management sentiment, 
            and generate an alpha conviction score — all powered by AI.
        </p>
    </div>
    """, unsafe_allow_html=True)
