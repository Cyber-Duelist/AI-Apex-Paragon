"""
SmartLedger AI — Receipt & Invoice Intelligence
Upload any receipt image → AI extracts items, categorizes spending, and gives saving advice.
Powered by Groq Vision (llama-4-scout-17b)
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

st.set_page_config(
    page_title="SmartLedger AI",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* Global background */
.stApp {
    background: linear-gradient(135deg, #060b18 0%, #0a1020 40%, #060e1a 100%) !important;
}
.main .block-container {
    padding-top: 2rem !important;
    max-width: 1200px !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6, 11, 24, 0.95) !important;
    border-right: 1px solid rgba(99,179,237,0.1) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1a56db, #0ea5e9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.25) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(14,165,233,0.4) !important;
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploadDropzone"] {
    background: rgba(14, 165, 233, 0.04) !important;
    border: 2px dashed rgba(14,165,233,0.3) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(14,165,233,0.6) !important;
    background: rgba(14, 165, 233, 0.08) !important;
}
[data-testid="stFileUploader"] label { color: #94a3b8 !important; font-weight: 600; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(99,179,237,0.1) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    padding: 16px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: transparent !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
iframe { background: transparent !important; }

/* ── Metric widget ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(99,179,237,0.12) !important;
    border-radius: 16px !important;
    padding: 20px !important;
}
[data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }

/* ── Spinner ── */
.stSpinner > div { border-color: #0ea5e9 transparent transparent !important; }

/* ── Alert / Info boxes ── */
.stAlert {
    background: rgba(14,165,233,0.08) !important;
    border: 1px solid rgba(14,165,233,0.2) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL = "llama-3.1-8b-instant"

CATEGORY_COLORS = {
    "Food & Dining":      "#f59e0b",
    "Transport":          "#0ea5e9",
    "Utilities & Bills":  "#ef4444",
    "Shopping":           "#a855f7",
    "Health & Medical":   "#10b981",
    "Entertainment":      "#ec4899",
    "Education":          "#06b6d4",
    "Other":              "#64748b"
}

CATEGORY_ICONS = {
    "Food & Dining": "🍽️", "Transport": "🚗", "Utilities & Bills": "💡",
    "Shopping": "🛍️", "Health & Medical": "💊", "Entertainment": "🎬",
    "Education": "📚", "Other": "📦"
}

# ── Session State ─────────────────────────────────────────────────────────────
if "receipts" not in st.session_state:
    st.session_state.receipts = []
if "advice" not in st.session_state:
    st.session_state.advice = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_image(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def analyze_receipt(image: Image.Image) -> dict:
    if not client:
        return {"error": "No API key configured."}
    b64 = encode_image(image)
    prompt = """Analyze this receipt/invoice image. Extract ALL items and return ONLY a JSON object:
{
  "store": "Store name",
  "date": "Date if visible else null",
  "currency": "Currency symbol",
  "items": [{"name": "Item", "quantity": 1, "price": 9.99, "category": "Food & Dining"}],
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00
}
Categories: Food & Dining, Transport, Utilities & Bills, Shopping, Health & Medical, Entertainment, Education, Other.
Return ONLY valid JSON."""
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": prompt}
            ]}],
            temperature=0.1, max_tokens=1500
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"error": "Could not parse receipt. Try a clearer image."}
    except Exception as e:
        return {"error": str(e)}

def generate_advice(all_receipts: list) -> str:
    if not client or not all_receipts: return ""
    category_totals = {}
    total_spend = 0
    for receipt in all_receipts:
        for item in receipt.get("items", []):
            cat = item.get("category", "Other")
            price = item.get("price", 0) or 0
            category_totals[cat] = category_totals.get(cat, 0) + price
            total_spend += price
    summary = f"Total: {total_spend:.2f}\n" + "\n".join(
        f"- {c}: {a:.2f} ({a/total_spend*100:.1f}%)" for c, a in sorted(category_totals.items(), key=lambda x: -x[1])
    )
    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a sharp, direct personal finance advisor. Be specific and actionable."},
                {"role": "user", "content": f"Give 5 specific money-saving tips based on this spending. Reference actual amounts.\n\n{summary}"}
            ],
            temperature=0.7, max_tokens=700
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate advice: {e}"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 24px;">
        <div style="font-size:1.6rem; font-weight:800; background:linear-gradient(135deg,#38bdf8,#10b981);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:4px;">
            SmartLedger AI
        </div>
        <div style="font-size:0.8rem; color:#475569; letter-spacing:2px; text-transform:uppercase;">
            Receipt Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not GROQ_API_KEY:
        st.markdown("""<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                    border-radius:12px;padding:14px;color:#fca5a5;font-size:0.85rem;">
                    ⚠️ <b>GROQ_API_KEY</b> not found.<br>Add it in your environment.
                    </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
                    border-radius:12px;padding:14px;color:#6ee7b7;font-size:0.85rem;">
                    ✅ <b>AI Engine Online</b></div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:24px 0 12px;font-size:0.75rem;color:#475569;text-transform:uppercase;letter-spacing:2px;'>Session</div>", unsafe_allow_html=True)

    if st.session_state.receipts:
        total = sum(
            r.get("total") or sum(i.get("price", 0) for i in r.get("items", []))
            for r in st.session_state.receipts
        )
        r1, r2 = st.columns(2)
        with r1:
            st.metric("Receipts", len(st.session_state.receipts))
        with r2:
            st.metric("Tracked", f"${total:.0f}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.receipts = []
            st.session_state.advice = ""
            st.rerun()
    else:
        st.markdown("<div style='color:#334155;font-size:0.9rem;padding:12px 0;'>No receipts yet.</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:32px; padding:20px; background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.06); border-radius:16px;">
        <div style="font-size:0.75rem;color:#475569;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;">How It Works</div>
        <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="display:flex;gap:12px;align-items:flex-start;">
                <div style="width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,#1a56db,#0ea5e9);
                    display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700;color:white;flex-shrink:0;">1</div>
                <div style="color:#94a3b8;font-size:0.85rem;padding-top:4px;">Upload any receipt photo</div>
            </div>
            <div style="display:flex;gap:12px;align-items:flex-start;">
                <div style="width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,#7c3aed,#a855f7);
                    display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700;color:white;flex-shrink:0;">2</div>
                <div style="color:#94a3b8;font-size:0.85rem;padding-top:4px;">Groq Vision AI extracts every item & category</div>
            </div>
            <div style="display:flex;gap:12px;align-items:flex-start;">
                <div style="width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,#059669,#10b981);
                    display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:700;color:white;flex-shrink:0;">3</div>
                <div style="color:#94a3b8;font-size:0.85rem;padding-top:4px;">See charts & get AI saving tips</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── HERO HEADER ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 20px 0 40px;">
    <div style="display:inline-flex;align-items:center;gap:10px;background:rgba(14,165,233,0.08);
                border:1px solid rgba(14,165,233,0.2);border-radius:100px;padding:6px 18px;
                margin-bottom:20px;">
        <div style="width:8px;height:8px;border-radius:50%;background:#10b981;
                    box-shadow:0 0 8px #10b981;animation:pulse 2s infinite;"></div>
        <span style="color:#38bdf8;font-size:0.8rem;font-weight:600;letter-spacing:1px;">AI ENGINE ONLINE</span>
    </div>
    <h1 style="font-size:3.2rem;font-weight:800;margin:0;
               background:linear-gradient(135deg,#f8fafc 0%,#38bdf8 50%,#10b981 100%);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;">
        SmartLedger AI
    </h1>
    <p style="color:#475569;font-size:1.1rem;margin-top:12px;font-weight:400;">
        Point. Scan. Understand. Save.
    </p>
</div>
<style>
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
</style>
""", unsafe_allow_html=True)

# ── UPLOAD SECTION ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    tab1, tab2 = st.tabs(["📁 Upload Image", "📸 Take Photo"])
    
    with tab1:
        uploaded = st.file_uploader(
            "Drop your receipt or invoice image here",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="visible"
        )
        
    with tab2:
        camera_photo = st.camera_input("Take a picture of a receipt", label_visibility="visible")
        
    source = uploaded or camera_photo

    if source:
        image = Image.open(source).convert("RGB")
        with col_right:
            st.markdown("""
            <div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                        letter-spacing:2px;margin-bottom:12px;">Preview</div>
            """, unsafe_allow_html=True)
            st.image(image, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Analyze with AI Vision", use_container_width=True, type="primary"):
            with st.spinner("Reading your receipt with Groq Vision..."):
                result = analyze_receipt(image)
            if "error" in result:
                st.markdown(f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                            border-radius:12px;padding:16px;color:#fca5a5;">❌ {result['error']}</div>""",
                            unsafe_allow_html=True)
            elif not result.get("items"):
                st.markdown(f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
                            border-radius:12px;padding:16px;color:#fca5a5;">❌ No line items found. Are you sure this is a receipt?</div>""",
                            unsafe_allow_html=True)
            else:
                result["_id"] = len(st.session_state.receipts)
                st.session_state.receipts.append(result)
                st.session_state.advice = ""
                store = result.get("store", "Unknown Store")
                total = result.get("total") or sum(i.get("price", 0) for i in result.get("items", []))
                curr = result.get("currency", "$")
                st.markdown(f"""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                            border-radius:12px;padding:16px;color:#6ee7b7;margin-top:8px;">
                            ✅ <b>{store}</b> — {curr}{total:.2f} extracted successfully!</div>""",
                            unsafe_allow_html=True)
                st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.receipts:
    # Self-healing: remove any receipts that got saved with 0 items
    valid_receipts = [r for r in st.session_state.receipts if r.get("items")]
    if len(valid_receipts) != len(st.session_state.receipts):
        st.session_state.receipts = valid_receipts
        st.rerun()
        
    all_items = []
    for r in st.session_state.receipts:
        for item in r.get("items", []):
            all_items.append({
                "name": item.get("name", "Unknown"),
                "price": float(item.get("price") or 0),
                "category": item.get("category", "Other"),
                "store": r.get("store", "Unknown"),
                "currency": r.get("currency", "$")
            })

    df = pd.DataFrame(all_items)
    if df.empty or "price" not in df.columns:
        total_spend = 0
        category_totals = pd.DataFrame({"category": ["Unknown"], "price": [0]})
        currency = "$"
        top_cat = "Unknown"
        avg = 0
    else:
        total_spend = df["price"].sum()
        category_totals = df.groupby("category")["price"].sum().reset_index()
        currency = st.session_state.receipts[0].get("currency", "$")
        top_cat = category_totals.loc[category_totals["price"].idxmax(), "category"]
        avg = total_spend / len(st.session_state.receipts)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown("""<div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:16px;">Overview</div>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    cards = [
        (k1, "Total Spent", f"{currency}{total_spend:.2f}", "#38bdf8", "💳"),
        (k2, "Top Category", f"{CATEGORY_ICONS.get(top_cat,'📦')} {top_cat}", "#a78bfa", "📊"),
        (k3, "Items Tracked", str(len(all_items)), "#34d399", "📋"),
        (k4, "Avg per Receipt", f"{currency}{avg:.2f}", "#fb923c", "🧮"),
    ]
    for col, label, val, color, icon in cards:
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);
                        border-radius:20px;padding:24px 20px;text-align:center;
                        transition:all 0.3s;position:relative;overflow:hidden;">
                <div style="position:absolute;top:-20px;right:-10px;font-size:3.5rem;opacity:0.07;">{icon}</div>
                <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">{label}</div>
                <div style="font-size:1.6rem;font-weight:800;color:{color};line-height:1.2;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown("""<div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:16px;">Spending Breakdown</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    colors = [CATEGORY_COLORS.get(c, "#64748b") for c in category_totals["category"]]

    with c1:
        fig_pie = px.pie(
            category_totals, values="price", names="category",
            color_discrete_sequence=colors, hole=0.6
        )
        fig_pie.update_traces(
            textfont_color="white", textfont_size=12,
            marker=dict(line=dict(color="#060b18", width=3))
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=12)),
            margin=dict(t=10, b=10, l=0, r=0),
            annotations=[dict(text=f"<b>{currency}{total_spend:.0f}</b>", x=0.5, y=0.5,
                              font=dict(size=22, color="#f8fafc", family="Inter"),
                              showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with c2:
        cat_s = category_totals.sort_values("price", ascending=True)
        colors_bar = [CATEGORY_COLORS.get(c, "#64748b") for c in cat_s["category"]]
        fig_bar = go.Figure(go.Bar(
            x=cat_s["price"], y=cat_s["category"], orientation="h",
            marker=dict(color=colors_bar, line=dict(width=0)),
            text=[f"{currency}{v:.2f}" for v in cat_s["price"]],
            textposition="outside", textfont=dict(color="#94a3b8", size=12),
            hovertemplate="<b>%{y}</b><br>%{x:.2f}<extra></extra>"
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.04)"),
            margin=dict(t=10, b=10, l=0, r=60), bargap=0.3
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ── Item Tables ───────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:16px;">Extracted Items</div>""", unsafe_allow_html=True)

    for receipt in st.session_state.receipts:
        store = receipt.get("store", "Receipt")
        date = receipt.get("date", "")
        curr = receipt.get("currency", "$")
        total = receipt.get("total") or sum(i.get("price", 0) for i in receipt.get("items", []))
        label = f"📄 {store}" + (f" · {date}" if date else "") + f" · **{curr}{total:.2f}**"

        with st.expander(label, expanded=len(st.session_state.receipts) == 1):
            items = receipt.get("items", [])
            if items:
                items_df = pd.DataFrame(items)
                items_df["price_fmt"] = items_df["price"].apply(lambda x: f"{curr}{float(x or 0):.2f}")
                display = items_df[["name", "category", "price_fmt", "quantity"]].copy()
                display.columns = ["Item", "Category", "Price", "Qty"]
                st.dataframe(
                    display, use_container_width=True, hide_index=True,
                    column_config={
                        "Item": st.column_config.TextColumn(width="large"),
                        "Category": st.column_config.TextColumn(width="medium"),
                        "Price": st.column_config.TextColumn(width="small"),
                        "Qty": st.column_config.NumberColumn(width="small"),
                    }
                )

    # ── AI Advice ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:16px;">AI Financial Advisor</div>""", unsafe_allow_html=True)

    if st.button("💡 Generate Personalized Saving Tips", use_container_width=True):
        with st.spinner("Analyzing your spending patterns..."):
            st.session_state.advice = generate_advice(st.session_state.receipts)

    if st.session_state.advice:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(16,185,129,0.06),rgba(14,165,233,0.06));
                    border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:28px;margin-top:8px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                <div style="width:36px;height:36px;border-radius:10px;
                            background:linear-gradient(135deg,#059669,#0ea5e9);
                            display:flex;align-items:center;justify-content:center;font-size:1.1rem;">💡</div>
                <div style="font-size:1rem;font-weight:700;color:#f0fdf4;">Your Personalized Money-Saving Tips</div>
            </div>
            <div style="color:#94a3b8;line-height:1.8;font-size:0.95rem;">
                {st.session_state.advice.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # ── Empty State ───────────────────────────────────────────────────────────
    chips_html = "".join([
        f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:10px 18px;color:#475569;font-size:0.85rem;">{icon} {name}</div>'
        for name, icon in [("Grocery","🛒"),("Restaurant","🍽️"),("Utility Bill","💡"),("Pharmacy","💊"),("Online Order","📦")]
    ])
    st.markdown(f"""
    <div style="text-align:center;padding:60px 40px;margin-top:20px;">
        <div style="width:80px;height:80px;border-radius:24px;
                    background:linear-gradient(135deg,rgba(14,165,233,0.1),rgba(16,185,129,0.1));
                    border:1px solid rgba(14,165,233,0.2);
                    display:flex;align-items:center;justify-content:center;
                    font-size:2.5rem;margin:0 auto 24px;">🧾</div>
        <h3 style="color:#475569;font-weight:600;margin-bottom:8px;">Upload your first receipt</h3>
        <p style="color:#334155;font-size:0.95rem;max-width:400px;margin:0 auto;">
            Supports grocery bills, restaurant receipts, utility invoices, online order summaries and more.
        </p>
        <div style="display:flex;gap:12px;justify-content:center;margin-top:28px;flex-wrap:wrap;">
            {chips_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
