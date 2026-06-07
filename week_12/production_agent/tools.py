import random
import json

# ==========================================
# 1. MOCK DATABASE
# ==========================================
KNOWLEDGE_BASE = [
    {"title": "Merger Agreement", "department": "Legal", "pages": 105, "content": "Confidential merger details between Company A and Company B."},
    {"title": "Q3 Financial Report", "department": "Finance", "pages": 120, "content": "Quarterly earnings and revenue projections."},
    {"title": "Employee Handbook", "department": "HR", "pages": 45, "content": "Standard operating procedures and code of conduct."},
    {"title": "Vendor Contract", "department": "Legal", "pages": 15, "content": "Agreement with IT service provider."},
    {"title": "Tax Audit 2023", "department": "Finance", "pages": 250, "content": "IRS audit findings and compliance notes."},
    {"title": "Onboarding Guide", "department": "HR", "pages": 10, "content": "Welcome guide for new hires."},
    {"title": "Non-Disclosure Agreement", "department": "Legal", "pages": 8, "content": "Standard NDA for contractors."},
    {"title": "Cloud Architecture", "department": "Engineering", "pages": 60, "content": "AWS deployment diagrams and security policies."}
]

# ==========================================
# 2. TOOLS
# ==========================================
def search_knowledge_base(query: str) -> dict:
    """Searches the knowledge base and returns relevant documents."""
    query_words = set(query.lower().split())
    results = []
    for doc in KNOWLEDGE_BASE:
        doc_text = f"{doc['title']} {doc['department']} {doc['content']}".lower()
        if any(word in doc_text for word in query_words):
            results.append(doc)
    return {"results": results[:3]}

def assess_document_risk(title: str, department: str, num_pages: int) -> dict:
    """Calculates risk level."""
    if department.lower() == "legal" and num_pages > 50:
        return {"risk_level": "high", "risk_score": 0.9}
    elif department.lower() == "finance" and num_pages > 100:
        return {"risk_level": "high", "risk_score": 0.85}
    return {"risk_level": "low", "risk_score": 0.2}

def get_compliance_policy(department: str) -> dict:
    policies = {"Legal": "Docs > 50 pages require senior review.", "Finance": "Docs > 100 pages require CFO approval."}
    return {"policy": policies.get(department.capitalize(), "Standard review applies.")}

def create_escalation_ticket(title: str, risk_level: str, reason: str) -> dict:
    return {"ticket_id": f"ESC-{random.randint(100, 999)}", "status": "created"}

def send_notification(recipient: str, subject: str, message: str) -> dict:
    return {"sent": True, "recipient": recipient}

AVAILABLE_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "assess_document_risk": assess_document_risk,
    "get_compliance_policy": get_compliance_policy,
    "create_escalation_ticket": create_escalation_ticket,
    "send_notification": send_notification
}

# ==========================================
# 3. REFINED TOOL SCHEMAS
# ==========================================
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Always call this first to get document metadata (department, pages) before risk assessment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The document title or keywords."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_document_risk",
            "description": "Assesses risk. REQUIRED: Use search_knowledge_base first to get accurate department and num_pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "department": {"type": "string"},
                    "num_pages": {"type": "integer"}
                },
                "required": ["title", "department", "num_pages"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_compliance_policy",
            "description": "Gets department policy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {"type": "string"}
                },
                "required": ["department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_escalation_ticket",
            "description": "Creates a ticket for high risk items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "risk_level": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["title", "risk_level", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_notification",
            "description": "Sends email notification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string"},
                    "subject": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["recipient", "subject", "message"]
            }
        }
    }
]