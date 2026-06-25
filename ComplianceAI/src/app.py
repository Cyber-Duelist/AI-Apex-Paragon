import streamlit as st
import os
import sys

# Ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from auth import render_auth_page, check_auth, logout
from database import init_db

# Initialize database on first run
init_db()

st.set_page_config(
    page_title="ComplianceAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: #e94560;
        font-size: 2.5rem;
        margin: 0;
    }
    .main-header p {
        color: #a0a0b0;
        font-size: 1.1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-card h3 {
        color: #e94560;
        font-size: 2rem;
        margin: 0;
    }
    .metric-card p {
        color: #a0a0b0;
        margin: 0.5rem 0 0 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #e94560, #c81d4e);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not check_auth():
    render_auth_page()
    st.stop()

# Authenticated user - show sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('username', 'User')}")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📄 Documents", "💬 Chat Agent", "📋 Reports"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# Page routing
if page == "📊 Dashboard":
    exec(open(os.path.join(current_dir, "pages", "1_Dashboard.py"), encoding="utf-8").read())
elif page == "📄 Documents":
    exec(open(os.path.join(current_dir, "pages", "2_Documents.py"), encoding="utf-8").read())
elif page == "💬 Chat Agent":
    exec(open(os.path.join(current_dir, "pages", "3_Chat.py"), encoding="utf-8").read())
elif page == "📋 Reports":
    exec(open(os.path.join(current_dir, "pages", "4_Reports.py"), encoding="utf-8").read())
