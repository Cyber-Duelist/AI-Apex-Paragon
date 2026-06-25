import streamlit as st
import os
import sys

# Ensure imports work regardless of execution directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agent import ProductionAgent

st.set_page_config(page_title="Enterprise Compliance Agent", page_icon="🛡️", layout="centered")

st.title("🛡️ Enterprise Compliance Agent")
st.markdown("An autonomous AI agent with **Input/Output Guardrails**, Tool Calling, and Persistent Memory. It analyzes documents, assesses risk, and escalates automatically.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Agent Configuration")
    
    # Check if API key is already in the environment (like Hugging Face Secrets)
    env_api_key = os.environ.get("GROQ_API_KEY", "")
    
    groq_api_key = st.text_input(
        "Groq API Key", 
        value=env_api_key,
        type="password", 
        help="Required to run the agent. Get one for free at console.groq.com"
    )
    
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
        
    st.markdown("---")
    st.markdown("**Tools Available:**")
    st.markdown("- 🔍 Knowledge Base Search\n- ⚖️ Risk Assessment\n- 📜 Compliance Policy Lookup\n- 🎫 Create Escalation Ticket\n- ✉️ Send Notification")

if not os.environ.get("GROQ_API_KEY"):
    st.warning("Please enter your Groq API Key in the sidebar to interact with the Agent.")
    st.stop()

# Initialize Agent
if "agent" not in st.session_state:
    try:
        with st.spinner("Initializing Model Failover Router..."):
            st.session_state.agent = ProductionAgent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
    st.session_state.messages.append({"role": "assistant", "content": "System initialized. Guardrails active. Please provide a document task for compliance review (e.g., 'Analyze the Merger Agreement from Legal with 105 pages. Escalate if high risk.')."})

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if prompt := st.chat_input("Enter your task here..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process via Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing input against Guardrails and executing multi-step tools..."):
            try:
                response = st.session_state.agent.process_request(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Execution Error: {e}")
