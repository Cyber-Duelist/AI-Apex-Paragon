import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database import get_user_stats, get_user_analyses, get_user_documents

user_id = st.session_state.get("user_id")

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ ComplianceAI</h1>
    <p>Enterprise Document Compliance Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# Stats
stats = get_user_stats(user_id)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{stats['total_docs']}</h3>
        <p>📄 Documents</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{stats['total_analyses']}</h3>
        <p>🔍 Analyses</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_risk = round(stats['avg_risk'] * 100) if stats['avg_risk'] else 0
    risk_color = "#4ade80" if avg_risk < 40 else "#facc15" if avg_risk < 70 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: {risk_color}">{avg_risk}%</h3>
        <p>⚖️ Avg Risk</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{stats['open_tickets']}</h3>
        <p>🎫 Open Tickets</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Two column layout
left, right = st.columns(2)

with left:
    st.subheader("📈 Recent Analyses")
    analyses = get_user_analyses(user_id)
    if analyses:
        for a in analyses[:5]:
            risk_emoji = "🔴" if a["risk_level"] == "high" else "🟡" if a["risk_level"] == "medium" else "🟢"
            st.markdown(f"{risk_emoji} **{a['framework']}** — Risk: `{a['risk_level']}` ({round(a['risk_score'] * 100)}%) — {a['created_at'][:10]}")
    else:
        st.info("No analyses yet. Upload a document and run your first compliance check!")

with right:
    st.subheader("📄 Your Documents")
    docs = get_user_documents(user_id)
    if docs:
        for d in docs[:5]:
            status_emoji = "✅" if d["status"] == "indexed" else "📤"
            st.markdown(f"{status_emoji} **{d['filename']}** — {d['page_count']} pages — {d['upload_date'][:10]}")
    else:
        st.info("No documents uploaded yet. Go to the Documents page to get started!")

# Quick start guide
st.markdown("---")
st.subheader("🚀 Quick Start")
st.markdown("""
1. **📄 Upload** a PDF or TXT document in the **Documents** page
2. **🔍 Analyze** it against GDPR, SOX, or HIPAA compliance frameworks
3. **💬 Chat** with the AI agent about your documents
4. **📋 Download** professional compliance reports
""")
