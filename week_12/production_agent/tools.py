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
# 2. DEFINE THE TOOLS (Python Functions)
# ==========================================
def search_knowledge_base(query: str) -> dict:
    """Searches a hardcoded list of 8 documents, returns top 3 matches by keyword overlap."""
    query_words = set(query.lower().split())
    scored_docs = []
    
    for doc in KNOWLEDGE_BASE:
        # Combine all text fields to search against
        doc_text = f"{doc['title']} {doc['department']} {doc['content']}".lower()
        # Count how many query words appear in the document text
        score = sum(1 for word in query_words if word in doc_text)
        scored_docs.append((score, doc))
        
    # Sort by highest score first and grab the top 3
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_3 = [doc for score, doc in scored_docs[:3]]
    
    return {"results": top_3}

def assess_document_risk(title: str, department: str, num_pages: int) -> dict:
    """Calculates risk level based on strict compliance rules."""
    dept = department.lower()
    
    if dept == "legal" and num_pages > 50:
        return {"risk_level": "high", "risk_score": 0.9}
    elif dept == "finance" and num_pages > 100:
        return {"risk_level": "high", "risk_score": 0.85}
    else:
        return {"risk_level": "low", "risk_score": 0.2}

def get_compliance_policy(department: str) -> dict:
    """Returns hardcoded compliance policies per department."""
    policies = {
        "Legal": "All documents over 50 pages require senior review.",
        "Finance": "All high-risk documents require CFO approval.",
        "HR": "Standard review process applies."
    }
    # Capitalize to ensure matching
    return {"policy": policies.get(department.capitalize(), "Standard company policy applies.")}

def create_escalation_ticket(title: str, risk_level: str, reason: str) -> dict:
    """Mocks creating a Jira/ServiceNow ticket."""
    ticket_id = f"ESC-{random.randint(100, 999)}"
    priority = "high" if risk_level.lower() == "high" else "medium"
    return {"ticket_id": ticket_id, "status": "created", "priority": priority}

def send_notification(recipient: str, subject: str, message: str) -> dict:
    """Mocks sending an email notification."""
    msg_id = f"MSG-{random.randint(100, 999)}"
    return {"sent": True, "recipient": recipient, "message_id": msg_id}


# ==========================================
# 3. MAP FUNCTIONS FOR THE AGENT ROUTER
# ==========================================
AVAILABLE_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "assess_document_risk": assess_document_risk,
    "get_compliance_policy": get_compliance_policy,
    "create_escalation_ticket": create_escalation_ticket,
    "send_notification": send_notification
}


# ==========================================
# 4. DEFINE THE TOOL SCHEMAS FOR GROQ
# ==========================================
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Searches the corporate knowledge base for documents matching a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keywords to search for, e.g., 'Merger Legal'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_document_risk",
            "description": "Calculates the risk level and score of a specific document.",
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
            "description": "Retrieves the standard operating policy for a department.",
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
            "description": "Escalates a document to management by creating a tracking ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "risk_level": {"type": "string"},
                    "reason": {"type": "string", "description": "Detailed reason for escalation."}
                },
                "required": ["title", "risk_level", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_notification",
            "description": "Sends an email notification to a specific recipient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Email address"},
                    "subject": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["recipient", "subject", "message"]
            }
        }
    }
]

# ==========================================
# 5. TEST BLOCK
# ==========================================
if __name__ == "__main__":
    print("=== TESTING ALL TOOLS ===")
    
    # 1. Search
    res_search = search_knowledge_base("Merger details")
    print(f"search_knowledge_base    : {res_search}")
    
    # 2. Assess Risk
    res_risk = assess_document_risk("Merger Agreement", "Legal", 105)
    print(f"assess_document_risk     : {res_risk}")
    
    # 3. Policy
    res_policy = get_compliance_policy("Legal")
    print(f"get_compliance_policy    : {res_policy}")
    
    # 4. Ticket
    res_ticket = create_escalation_ticket("Merger Agreement", "high", "High risk document.")
    print(f"create_escalation_ticket : {res_ticket}")
    
    # 5. Notification
    res_notify = send_notification("compliance@company.com", "Ticket Created", "Please review.")
    print(f"send_notification        : {res_notify}")