import os
import sys
import json
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from vector_store import get_collection, search
from compliance_engine import analyze_document
import database

def search_documents(query: str, user_id: int) -> dict:
    """Search user's uploaded documents using semantic search."""
    collection = get_collection(user_id=user_id)
    results = search(query, collection, top_k=3)
    if not results:
        return {'results': [], 'message': 'No matching documents found. Please upload documents first.'}
    return {'results': [{'text': r['text'][:200], 'source': r['metadata']['source'], 'page': r['metadata']['page']} for r in results]}

def analyze_compliance(document_name: str, framework: str, user_id: int) -> dict:
    """Run compliance analysis on a specific document."""
    collection = get_collection(user_id=user_id)
    # Get all chunks for this document
    results = search(document_name, collection, top_k=10)
    doc_results = [r for r in results if r['metadata']['source'] == document_name]
    if not doc_results:
        # Try broader search
        doc_results = results[:5] if results else []
    if not doc_results:
        return {'error': f'Document "{document_name}" not found. Please upload it first.'}
    
    full_text = '\n'.join([r['text'] for r in doc_results])
    analysis = analyze_document(full_text, framework=framework)
    
    # Store in database
    docs = database.get_user_documents(user_id)
    doc_id = None
    for d in docs:
        if d['filename'] == document_name:
            doc_id = d['id']
            break
    if doc_id:
        database.add_analysis(doc_id, user_id, framework, analysis['risk_score'], analysis['risk_level'], json.dumps(analysis['findings']), '\n'.join(analysis['recommendations']))
    
    return analysis

def get_risk_summary(user_id: int) -> dict:
    """Get risk summary across all user's documents."""
    stats = database.get_user_stats(user_id)
    analyses = database.get_user_analyses(user_id)
    return {
        'total_documents': stats['total_docs'],
        'total_analyses': stats['total_analyses'],
        'average_risk_score': round(stats['avg_risk'], 2) if stats['avg_risk'] else 0,
        'open_tickets': stats['open_tickets'],
        'recent_analyses': [{'framework': a['framework'], 'risk_level': a['risk_level'], 'risk_score': a['risk_score']} for a in analyses[:5]]
    }

def create_ticket(title: str, priority: str, user_id: int) -> dict:
    """Create an escalation ticket."""
    analyses = database.get_user_analyses(user_id)
    analysis_id = analyses[0]['id'] if analyses else None
    ticket_id = database.add_ticket(analysis_id, user_id, title, priority)
    return {'ticket_id': ticket_id, 'status': 'open', 'priority': priority, 'message': f'Escalation ticket #{ticket_id} created successfully.'}

def send_notification(recipient: str, subject: str, message: str) -> dict:
    """Simulate sending a notification."""
    msg_id = f'MSG-{random.randint(1000, 9999)}'
    return {'sent': True, 'recipient': recipient, 'message_id': msg_id, 'note': 'Notification simulated for demo purposes.'}


TOOL_SCHEMAS = [
    {
        'type': 'function',
        'function': {
            'name': 'search_documents',
            'description': 'Search the user uploaded documents in the knowledge base using semantic search',
            'parameters': {'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Search query'}}, 'required': ['query']}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'analyze_compliance',
            'description': 'Run compliance analysis on a document against a framework (GDPR, SOX, or HIPAA)',
            'parameters': {'type': 'object', 'properties': {'document_name': {'type': 'string'}, 'framework': {'type': 'string', 'enum': ['GDPR', 'SOX', 'HIPAA']}}, 'required': ['document_name', 'framework']}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_risk_summary',
            'description': 'Get a summary of risk scores and compliance status across all documents',
            'parameters': {'type': 'object', 'properties': {}, 'required': []}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'create_ticket',
            'description': 'Create an escalation ticket for a compliance issue',
            'parameters': {'type': 'object', 'properties': {'title': {'type': 'string'}, 'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']}}, 'required': ['title', 'priority']}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'send_notification',
            'description': 'Send an email notification to a stakeholder',
            'parameters': {'type': 'object', 'properties': {'recipient': {'type': 'string'}, 'subject': {'type': 'string'}, 'message': {'type': 'string'}}, 'required': ['recipient', 'subject', 'message']}
        }
    }
]

AVAILABLE_FUNCTIONS = {
    'search_documents': search_documents,
    'analyze_compliance': analyze_compliance,
    'get_risk_summary': get_risk_summary,
    'create_ticket': create_ticket,
    'send_notification': send_notification
}
