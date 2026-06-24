"""
SentinelAlpha — Scoring & Visualization Engine
Processes raw LLM analysis into numerical scores and Plotly chart configs.
"""

import plotly.graph_objects as go
from config import CONVICTION_COLORS, HEDGE_WORDS


def build_conviction_gauge(score: int, label: str) -> go.Figure:
    """Create a Plotly gauge chart for the conviction score (-100 to 100)."""
    color = CONVICTION_COLORS.get(label, "#ffffff")
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"font": {"size": 60, "color": color}},
        title={"text": f"<b>{label}</b>", "font": {"size": 24, "color": color}},
        gauge={
            "axis": {"range": [-100, 100], "tickwidth": 2, "tickcolor": "#333"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 2,
            "bordercolor": "#333",
            "steps": [
                {"range": [-100, -60], "color": "rgba(255, 34, 51, 0.15)"},
                {"range": [-60, -20], "color": "rgba(255, 102, 68, 0.12)"},
                {"range": [-20, 20], "color": "rgba(255, 170, 0, 0.10)"},
                {"range": [20, 60], "color": "rgba(0, 204, 102, 0.12)"},
                {"range": [60, 100], "color": "rgba(0, 255, 136, 0.15)"},
            ],
            "threshold": {
                "line": {"color": "#fff", "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#ccc", "family": "JetBrains Mono, monospace"},
        height=350,
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig


def build_risk_radar(risk_factors: list[dict]) -> go.Figure:
    """Create a radar chart of risk categories and their severity."""
    categories = {}
    severity_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    
    for rf in risk_factors:
        cat = rf.get("category", "Other")
        sev = severity_map.get(rf.get("severity", "LOW"), 1)
        categories[cat] = max(categories.get(cat, 0), sev)
    
    if not categories:
        categories = {"Market": 1, "Regulatory": 1, "Operational": 1}
    
    labels = list(categories.keys())
    values = list(categories.values())
    # Close the polygon
    labels.append(labels[0])
    values.append(values[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        fillcolor='rgba(255, 51, 102, 0.15)',
        line=dict(color='#ff3366', width=2),
        marker=dict(size=8, color='#ff3366'),
        name='Risk Severity'
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 3.5],
                ticktext=["", "LOW", "MEDIUM", "HIGH"],
                tickvals=[0, 1, 2, 3],
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.1)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", family="JetBrains Mono, monospace"),
        showlegend=False,
        height=400,
        margin=dict(l=60, r=60, t=40, b=40),
    )
    return fig


def build_sentiment_bar(sec_score: float, earnings_score: float, conviction_score: int) -> go.Figure:
    """Horizontal bar chart comparing sentiment across all 3 modules."""
    labels = ["SEC Filing Sentiment", "Earnings Call Sentiment", "Conviction Score"]
    # Normalize conviction to -1 to 1 scale
    values = [sec_score, earnings_score, conviction_score / 100.0]
    colors = [
        "#00e5ff" if v >= 0 else "#ff3366" for v in values
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=1),
        ),
        text=[f"{v:+.2f}" for v in values],
        textposition='auto',
        textfont=dict(color='#fff', size=14),
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", family="JetBrains Mono, monospace"),
        xaxis=dict(
            range=[-1.1, 1.1],
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.3)",
            zerolinewidth=2,
            title="Bearish ← → Bullish",
        ),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=250,
        margin=dict(l=10, r=10, t=20, b=40),
    )
    return fig


def build_hedge_word_chart(hedge_data: dict) -> go.Figure:
    """Gauge showing hedge word density."""
    density_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    val = density_map.get(hedge_data.get("density_label", "LOW"), 1)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=hedge_data.get("count", 0),
        number={"suffix": " words", "font": {"size": 36, "color": "#ffaa00"}},
        title={"text": f"Hedge Word Density: {hedge_data.get('density_label', 'N/A')}", "font": {"size": 16, "color": "#ccc"}},
        gauge={
            "axis": {"range": [0, 30], "tickcolor": "#333"},
            "bar": {"color": "#ffaa00", "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 2,
            "bordercolor": "#333",
            "steps": [
                {"range": [0, 8], "color": "rgba(0, 255, 136, 0.1)"},
                {"range": [8, 15], "color": "rgba(255, 170, 0, 0.1)"},
                {"range": [15, 22], "color": "rgba(255, 102, 68, 0.1)"},
                {"range": [22, 30], "color": "rgba(255, 34, 51, 0.1)"},
            ],
        },
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ccc", family="JetBrains Mono, monospace"),
        height=280,
        margin=dict(l=30, r=30, t=50, b=20),
    )
    return fig


def count_hedge_words(text: str) -> dict:
    """Count hedge words in a text and return analysis."""
    text_lower = text.lower()
    found = []
    count = 0
    for word in HEDGE_WORDS:
        occurrences = text_lower.count(word.lower())
        if occurrences > 0:
            count += occurrences
            found.append(word)
    
    if count <= 5:
        density = "LOW"
    elif count <= 12:
        density = "MEDIUM"
    elif count <= 20:
        density = "HIGH"
    else:
        density = "CRITICAL"
    
    return {"count": count, "density_label": density, "examples": found}
