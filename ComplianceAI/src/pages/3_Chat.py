import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from agent import ComplianceAgent
from database import check_rate_limit, increment_usage

user_id = st.session_state.get("user_id")

st.header("💬 Compliance Chat Agent")
st.markdown("Ask questions about your documents, check compliance, or escalate issues.")

if not check_rate_limit(user_id):
    st.error("⚠️ Daily query limit reached (20/day). Please try again tomorrow.")
    st.stop()

# Initialize Agent
if "agent" not in st.session_state:
    try:
        with st.spinner("Initializing Agent..."):
            st.session_state.agent = ComplianceAgent(user_id=user_id)
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I am ComplianceAI. How can I help you analyze your documents today?"
    })

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if prompt := st.chat_input("Ask a question (e.g., 'Check the risk level of my new contract')"):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process via Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and executing..."):
            try:
                increment_usage(user_id)
                response = st.session_state.agent.process_request(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Execution Error: {e}")
