"""
SmartLedger AI — Receipt & Invoice Intelligence
Upload any receipt image → AI extracts items, categorizes spending, and gives saving advice.
Powered by Groq Vision (llama-3.2-11b-vision-preview)
"""

import os
import json
import base64
import io
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartLedger AI",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0a0e1a; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a1628 100%); }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(16,24,48,0.9), rgba(10,18,36,0.95));
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(99,179,237,0.5); transform: translateY(-2px); }
.metric-value { font-size: 2rem; font-weight: 700; color: #63b3ed; margin: 0; }
.metric-label { font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 1px; margin: 4px 0 0; }

/* Item table */
.item-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid rgba(99,179,237,0.08);
    border-radius: 8px;
    transition: background 0.2s;
}
.item-row:hover { background: rgba(99,179,237,0.05); }
.item-name { color: #e2e8f0; font-size: 0.95rem; }
.item-price { color: #68d391; font-weight: 600; }
.item-cat { font-size: 0.75rem; color: #805ad5; background: rgba(128,90,213,0.1); padding: 2px 8px; border-radius: 20px; }

/* Advice card */
.advice-card {
    background: linear-gradient(135deg, rgba(72,187,120,0.08), rgba(49,130,206,0.08));
    border: 1px solid rgba(72,187,120,0.2);
    border-radius: 16px;
    padding: 24px;
    margin-top: 16px;
}
.advice-title { color: #68d391; font-size: 1rem; font-weight: 600; margin-bottom: 12px; }

/* Hero */
.hero { text-align: center; padding: 40px 0 20px; }
.hero h1 { font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #63b3ed, #68d391); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color: #718096; font-size: 1.1rem; margin-top: 8px; }

/* Upload zone */
.upload-zone { background: rgba(16,24,48,0.6); border: 2px dashed rgba(99,179,237,0.3); border-radius: 16px; padding: 40px; text-align: center; }

/* Category badge colors */
.cat-food { color: #f6ad55; background: rgba(246,173,85,0.1); }
.cat-transport { color: #63b3ed; background: rgba(99,179,237,0.1); }
.cat-utilities { color: #fc8181; background: rgba(252,129,129,0.1); }
.cat-shopping { color: #b794f4; background: rgba(183,148,244,0.1); }
.cat-health { color: #68d391; background: rgba(104,211,145,0.1); }
.cat-other { color: #a0aec0; background: rgba(160,174,192,0.1); }

div[data-testid="stSidebarContent"] { background: rgba(10, 14, 26, 0.95); }
</style>
""", unsafe_allow_html=True)

# ── Groq Setup ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama-3.1-8b-instant"

CATEGORY_COLORS = {
    "Food & Dining": "#f6ad55",
    "Transport": "#63b3ed",
    "Utilities & Bills": "#fc8181",
    "Shopping": "#b794f4",
    "Health & Medical": "#68d391",
    "Entertainment": "#f687b3",
    "Education": "#76e4f7",
    "Other": "#a0aec0"
}

# ── Session State ─────────────────────────────────────────────────────────────
if "receipts" not in st.session_state:
    st.session_state.receipts = []  # list of parsed receipt dicts
if "advice" not in st.session_state:
    st.session_state.advice = ""

# ── Helper: encode image ──────────────────────────────────────────────────────
def encode_image(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# ── Core: Analyze Receipt ─────────────────────────────────────────────────────
def analyze_receipt(image: Image.Image) -> dict:
    if not client:
        return {"error": "No API key configured."}

    b64 = encode_image(image)
    prompt = """Analyze this receipt/invoice image. Extract ALL items and return a JSON object with this exact structure:
{
  "store": "Store/vendor name",
  "date": "Date if visible, else null",
  "currency": "Currency symbol (e.g. $, ₹, £)",
  "items": [
    {
      "name": "Item name",
      "quantity": 1,
      "price": 9.99,
      "category": "One of: Food & Dining, Transport, Utilities & Bills, Shopping, Health & Medical, Entertainment, Education, Other"
    }
  ],
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00
}

Rules:
- If a field is not visible, use null
- price must be a number (not string)
- Extract EVERY line item visible
- Be accurate with amounts
- Return ONLY the JSON, no explanation"""

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    {"type": "text", "text": prompt}
                ]
            }],
            temperature=0.1,
            max_tokens=1500
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"error": "Could not parse receipt. Please try a clearer image."}
    except Exception as e:
        return {"error": str(e)}

# ── Core: Generate Saving Advice ──────────────────────────────────────────────
def generate_advice(all_receipts: list) -> str:
    if not client or not all_receipts:
        return ""

    # Build spending summary
    category_totals = {}
    total_spend = 0
    for receipt in all_receipts:
        for item in receipt.get("items", []):
            cat = item.get("category", "Other")
            price = item.get("price", 0) or 0
            category_totals[cat] = category_totals.get(cat, 0) + price
            total_spend += price

    summary = f"Total spending: {total_spend:.2f}\n"
    for cat, amt in sorted(category_totals.items(), key=lambda x: -x[1]):
        pct = (amt / total_spend * 100) if total_spend > 0 else 0
        summary += f"- {cat}: {amt:.2f} ({pct:.1f}%)\n"

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{
                "role": "system",
                "content": "You are a sharp, friendly personal finance advisor. Be specific, actionable, and honest. Use emojis sparingly."
            }, {
                "role": "user",
                "content": f"""Based on this spending breakdown, give 4-5 specific, personalized money-saving tips. Be direct and practical.

{summary}

Format each tip as a bullet point. Reference actual categories and amounts from the data."""
            }],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate advice: {e}"

# ── UI: Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧾 SmartLedger AI")
    st.markdown("---")

    if not GROQ_API_KEY:
        st.error("⚠️ No API key found. Set `GROQ_API_KEY` in your environment.")
    else:
        st.success("✅ AI Engine Connected")

    st.markdown("### 📊 Session Summary")
    if st.session_state.receipts:
        total = sum(r.get("total") or sum(i.get("price", 0) for i in r.get("items", [])) for r in st.session_state.receipts)
        st.metric("Receipts Scanned", len(st.session_state.receipts))
        st.metric("Total Tracked", f"${total:.2f}")

        if st.button("🗑️ Clear All Receipts", use_container_width=True):
            st.session_state.receipts = []
            st.session_state.advice = ""
            st.rerun()
    else:
        st.info("No receipts scanned yet.")

    st.markdown("---")
    st.markdown("""
**How it works:**
1. Upload a receipt photo
2. AI extracts every item + category
3. See your spending breakdown
4. Get personalized saving tips

**Supported:** Grocery, restaurant, pharmacy, utility, shopping receipts
""")

# ── UI: Main ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🧾 SmartLedger AI</h1>
    <p>Upload receipts → AI extracts items → Understand your spending → Save more money</p>
</div>
""", unsafe_allow_html=True)

# Upload section
col_upload, col_preview = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("#### 📤 Upload Receipt or Invoice")
    uploaded = st.file_uploader(
        "Drop your receipt image here",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")

        with col_preview:
            st.markdown("#### 🔍 Receipt Preview")
            st.image(image, use_container_width=True)

        st.markdown("---")
        if st.button("🤖 Analyze with AI", use_container_width=True, type="primary"):
            with st.spinner("AI is reading your receipt... 🔍"):
                result = analyze_receipt(image)

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                result["_id"] = len(st.session_state.receipts)
                st.session_state.receipts.append(result)
                st.session_state.advice = ""  # reset advice
                st.success(f"✅ Receipt from **{result.get('store', 'Unknown Store')}** analyzed successfully!")
                st.rerun()

# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.receipts:
    st.markdown("---")

    # ── Aggregate All Data ────────────────────────────────────────────────────
    all_items = []
    for r in st.session_state.receipts:
        for item in r.get("items", []):
            all_items.append({
                "name": item.get("name", "Unknown"),
                "price": item.get("price") or 0,
                "category": item.get("category", "Other"),
                "store": r.get("store", "Unknown"),
                "currency": r.get("currency", "$")
            })

    df = pd.DataFrame(all_items)
    total_spend = df["price"].sum()
    category_totals = df.groupby("category")["price"].sum().reset_index()
    currency = st.session_state.receipts[0].get("currency", "$")

    # ── KPI Metrics ───────────────────────────────────────────────────────────
    st.markdown("#### 📊 Spending Overview")
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""<div class="metric-card">
            <p class="metric-value">{currency}{total_spend:.2f}</p>
            <p class="metric-label">Total Spent</p>
        </div>""", unsafe_allow_html=True)

    with m2:
        top_cat = category_totals.loc[category_totals["price"].idxmax(), "category"] if not category_totals.empty else "N/A"
        st.markdown(f"""<div class="metric-card">
            <p class="metric-value" style="font-size:1.2rem">{top_cat}</p>
            <p class="metric-label">Top Category</p>
        </div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""<div class="metric-card">
            <p class="metric-value">{len(all_items)}</p>
            <p class="metric-label">Items Tracked</p>
        </div>""", unsafe_allow_html=True)

    with m4:
        avg = total_spend / len(st.session_state.receipts) if st.session_state.receipts else 0
        st.markdown(f"""<div class="metric-card">
            <p class="metric-value">{currency}{avg:.2f}</p>
            <p class="metric-label">Avg per Receipt</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown("#### 🍩 Spending by Category")
        colors = [CATEGORY_COLORS.get(c, "#a0aec0") for c in category_totals["category"]]
        fig_pie = px.pie(
            category_totals,
            values="price",
            names="category",
            color_discrete_sequence=colors,
            hole=0.5
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
            margin=dict(t=20, b=20, l=0, r=0)
        )
        fig_pie.update_traces(textfont_color="#e2e8f0")
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown("#### 📊 Amount by Category")
        cat_sorted = category_totals.sort_values("price", ascending=True)
        colors_bar = [CATEGORY_COLORS.get(c, "#a0aec0") for c in cat_sorted["category"]]
        fig_bar = go.Figure(go.Bar(
            x=cat_sorted["price"],
            y=cat_sorted["category"],
            orientation="h",
            marker_color=colors_bar,
            text=[f"{currency}{v:.2f}" for v in cat_sorted["price"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0")
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(showgrid=False, showticklabels=False, color="#718096"),
            yaxis=dict(color="#a0aec0"),
            margin=dict(t=20, b=20, l=0, r=60)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Item Breakdown ────────────────────────────────────────────────────────
    st.markdown("#### 🧾 All Extracted Items")

    for receipt in st.session_state.receipts:
        with st.expander(f"📄 {receipt.get('store', 'Receipt')} — {receipt.get('date', 'No date')} | Total: {receipt.get('currency','$')}{receipt.get('total', 0):.2f}", expanded=True):
            items = receipt.get("items", [])
            if items:
                items_df = pd.DataFrame(items)[["name", "category", "price", "quantity"]]
                items_df.columns = ["Item", "Category", "Price", "Qty"]
                items_df["Price"] = items_df["Price"].apply(lambda x: f"{receipt.get('currency','$')}{x:.2f}")
                st.dataframe(
                    items_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Item": st.column_config.TextColumn(width="large"),
                        "Category": st.column_config.TextColumn(width="medium"),
                        "Price": st.column_config.TextColumn(width="small"),
                        "Qty": st.column_config.NumberColumn(width="small")
                    }
                )
            else:
                st.info("No items extracted from this receipt.")

    # ── AI Saving Advice ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 💡 AI Financial Advisor")

    if st.button("🤖 Generate Personalized Saving Tips", use_container_width=True):
        with st.spinner("Analyzing your spending habits... 💰"):
            st.session_state.advice = generate_advice(st.session_state.receipts)

    if st.session_state.advice:
        st.markdown(f"""<div class="advice-card">
            <p class="advice-title">💡 Your Personalized Money-Saving Advice</p>
            {st.session_state.advice.replace(chr(10), '<br>')}
        </div>""", unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; color: #4a5568;">
        <div style="font-size: 4rem; margin-bottom: 16px;">🧾</div>
        <h3 style="color: #718096;">Upload your first receipt to get started</h3>
        <p style="color: #4a5568;">Supports grocery bills, restaurant receipts, invoices, utility bills, and more.</p>
    </div>
    """, unsafe_allow_html=True)
