import streamlit as st
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database import get_user_analyses, get_user_documents
from report_generator import generate_compliance_report

user_id = st.session_state.get("user_id")

st.header("📋 Compliance Reports")
st.markdown("View completed analyses and download PDF reports.")

analyses = get_user_analyses(user_id)
docs = {d['id']: d['filename'] for d in get_user_documents(user_id)}

if not analyses:
    st.info("No analyses found. Go to the Documents page to run your first compliance check!")
else:
    for a in analyses:
        doc_name = docs.get(a['document_id'], f"Document #{a['document_id']}")
        
        with st.expander(f"📊 {doc_name} — {a['framework']} Analysis ({a['created_at'][:10]})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                risk_emoji = "🔴" if a['risk_level'] == 'high' else "🟡" if a['risk_level'] == 'medium' else "🟢"
                st.markdown(f"### {risk_emoji} Risk Level: **{a['risk_level'].upper()}**")
                st.progress(a['risk_score'])
                
                try:
                    findings = json.loads(a['findings'])
                except:
                    findings = [a['findings']]
                    
                st.markdown("**Findings:**")
                for f in findings:
                    st.markdown(f"- {f}")
                    
                st.markdown("**Recommendations:**")
                # Handle recommendations that might be stored as a single string with newlines
                recs = [r.strip() for r in a['recommendations'].split('\n') if r.strip('- ')]
                for r in recs:
                    st.markdown(f"- {r}")
                    
            with col2:
                # Generate PDF bytes
                pdf_bytes = generate_compliance_report(
                    doc_name=doc_name,
                    framework=a['framework'],
                    risk_score=a['risk_score'],
                    risk_level=a['risk_level'],
                    findings=findings,
                    recommendations=recs,
                    output_dir=None
                )
                
                safe_filename = f"{doc_name.replace('.pdf', '')}_{a['framework']}_Report.pdf"
                
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name=safe_filename,
                    mime="application/pdf",
                    key=f"dl_{a['id']}",
                    use_container_width=True
                )
