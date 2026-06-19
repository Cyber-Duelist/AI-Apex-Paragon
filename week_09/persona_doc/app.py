import streamlit as st
import os
import sys

# Ensure imports work regardless of execution directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from vector_store import get_collection, search
from hallucination_control import rag_with_guard
from ingest import ingest_document
from chunker import chunk_document
from vector_store import add_chunks

st.set_page_config(page_title="PersonaDoc - Production RAG", page_icon="📚", layout="centered")

st.title("📚 PersonaDoc")
st.markdown("A Production Retrieval-Augmented Generation (RAG) system with **Semantic Chunking**, **ChromaDB Vector Search**, and **Hallucination Control**.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Groq API Key", type="password", help="Required to run the agent. Get one for free at console.groq.com")
    st.markdown("---")
    st.markdown("**Upload a Document**")
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    
    if uploaded_file and groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
        if st.button("Index Document"):
            with st.spinner("Extracting text and chunking..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = os.path.join(current_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    pages = ingest_document(temp_path)
                    chunks = chunk_document(pages, chunk_size=400, overlap=80)
                    collection = get_collection()
                    add_chunks(chunks, collection)
                    os.remove(temp_path)
                    st.success(f"Indexed {len(chunks)} semantic chunks from {uploaded_file.name}!")
                except Exception as e:
                    st.error(f"Failed to index document: {e}")

if not groq_api_key:
    st.warning("Please enter your Groq API Key in the sidebar to interact with the RAG system.")
    st.stop()

os.environ["GROQ_API_KEY"] = groq_api_key

# Initialize Chat History
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []
    st.session_state.rag_messages.append({"role": "assistant", "content": "Welcome to PersonaDoc! Upload a document in the sidebar, or ask a question about previously indexed documents."})

# Display Chat
for msg in st.session_state.rag_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to UI
    st.session_state.rag_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process via RAG
    with st.chat_message("assistant"):
        with st.spinner("Searching vector database and generating grounded response..."):
            try:
                collection = get_collection()
                result = rag_with_guard(prompt, collection, model_name="llama-3.1-8b-instant")
                
                answer = result["answer"]
                if result.get("grounded"):
                    raw = search(prompt, collection, top_k=3)
                    citations = [f"{r['metadata']['source']} (Page {r['metadata']['page']})" for r in raw]
                    if citations:
                        answer += "\n\n**Citations:**\n" + "\n".join([f"- {c}" for c in set(citations)])
                else:
                    answer = "⚠️ **Warning: Hallucination Guardrail Triggered.** The model could not ground its answer in the provided documents.\n\n" + answer
                    
                st.markdown(answer)
                st.session_state.rag_messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Execution Error: {e}")
