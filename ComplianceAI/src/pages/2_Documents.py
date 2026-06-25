import streamlit as st
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from ingest import ingest_document
from chunker import chunk_document
from vector_store import get_collection, add_chunks, delete_document_chunks
from compliance_engine import analyze_document
from database import add_document, get_user_documents, delete_document, add_analysis, check_rate_limit, increment_usage

user_id = st.session_state.get("user_id")

st.header("📄 Document Management")

# Upload Section
st.subheader("⬆️ Upload Document")
uploaded_file = st.file_uploader(
    "Upload PDF or TXT file", 
    type=["pdf", "txt"],
    help="Upload a document to analyze for compliance"
)

if uploaded_file:
    if st.button("📥 Index Document", use_container_width=True):
        with st.spinner("Extracting text, chunking, and embedding..."):
            try:
                # Save temporarily
                temp_path = os.path.join(parent_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Ingest
                pages = ingest_document(temp_path)
                if not pages:
                    st.error("Could not extract text from this document.")
                else:
                    # Chunk
                    chunks = chunk_document(pages, chunk_size=400, overlap=80)
                    
                    # Embed & store
                    collection = get_collection(user_id=user_id)
                    add_chunks(chunks, collection)
                    
                    # Save metadata to DB
                    page_count = len(pages)
                    chunk_count = len(chunks)
                    add_document(user_id, uploaded_file.name, page_count, chunk_count)
                    
                    st.success(f"✅ Indexed **{uploaded_file.name}** — {page_count} pages, {chunk_count} chunks")
                
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# Document List
st.subheader("📋 Your Documents")
docs = get_user_documents(user_id)

if not docs:
    st.info("No documents uploaded yet. Upload your first document above!")
else:
    for doc in docs:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            
            with col1:
                st.markdown(f"**📄 {doc['filename']}**")
                st.caption(f"{doc['page_count']} pages • {doc.get('chunk_count', 'N/A')} chunks • Uploaded {doc['upload_date'][:10]}")
            
            with col2:
                status_color = "🟢" if doc["status"] == "indexed" else "🟡"
                st.markdown(f"{status_color} {doc['status'].title()}")
            
            with col3:
                framework = st.selectbox(
                    "Framework",
                    ["GDPR", "SOX", "HIPAA"],
                    key=f"fw_{doc['id']}",
                    label_visibility="collapsed"
                )
                
                if st.button("🔍 Analyze", key=f"analyze_{doc['id']}", use_container_width=True):
                    if not check_rate_limit(user_id):
                        st.error("Daily query limit reached (20/day). Please try again tomorrow.")
                    else:
                        with st.spinner(f"Analyzing against {framework}..."):
                            try:
                                # Get document text from chunks
                                collection = get_collection(user_id=user_id)
                                from vector_store import search
                                results = search(doc['filename'], collection, top_k=20)
                                doc_chunks = [r for r in results if r['metadata']['source'] == doc['filename']]
                                
                                if not doc_chunks:
                                    st.warning("No indexed content found. Please re-upload.")
                                else:
                                    full_text = "\n".join([r['text'] for r in doc_chunks])
                                    analysis = analyze_document(full_text, framework=framework)
                                    increment_usage(user_id)
                                    
                                    # Store analysis
                                    add_analysis(
                                        doc['id'], user_id, framework,
                                        analysis['risk_score'], analysis['risk_level'],
                                        json.dumps(analysis['findings']),
                                        "\n".join(analysis['recommendations'])
                                    )
                                    
                                    # Display results
                                    risk_emoji = "🔴" if analysis['risk_level'] == 'high' else "🟡" if analysis['risk_level'] == 'medium' else "🟢"
                                    st.markdown(f"### {risk_emoji} Risk: {analysis['risk_level'].upper()} ({round(analysis['risk_score'] * 100)}%)")
                                    
                                    st.markdown("**Findings:**")
                                    for finding in analysis['findings']:
                                        st.markdown(f"- {finding}")
                                    
                                    st.markdown("**Recommendations:**")
                                    for rec in analysis['recommendations']:
                                        st.markdown(f"- {rec}")
                                        
                            except Exception as e:
                                st.error(f"Analysis error: {e}")
            
            with col4:
                if st.button("🗑️", key=f"del_{doc['id']}", help="Delete document"):
                    try:
                        collection = get_collection(user_id=user_id)
                        delete_document_chunks(collection, doc['filename'])
                        delete_document(doc['id'], user_id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete error: {e}")
            
            st.markdown("---")
