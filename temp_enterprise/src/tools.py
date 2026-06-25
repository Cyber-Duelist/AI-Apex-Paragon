import random

# --- Tool Functions ---

def search_knowledge_base(query: str) -> dict:
    docs = [
        {"title": "Q3 Legal Review", "department": "Legal", "pages": 60},
        {"title": "Employee Handbook", "department": "HR", "pages": 20},
        {"title": "Financial Audit 2025", "department": "Finance", "pages": 120},
        {"title": "Tax Compliance", "department": "Finance", "pages": 40},
        {"title": "Merger Agreement", "department": "Legal", "pages": 80},
        {"title": "Security Policy", "department": "IT", "pages": 10},
        {"title": "Q4 Budget Planning", "department": "Finance", "pages": 150},
        {"title": "Hiring Strategy", "department": "HR", "pages": 5},
    ]
    query_words = query.lower().split()
    results = [
        d for d in docs 
        if any(word in d["title"].lower() or word in d["department"].lower() for word in query_words)
    ]
    return {"results": results[:3]}

def assess_document_risk(title: str, department: str, num_pages: int) -> dict:
    if department == "Legal" and num_pages > 50:
        return {"risk_level": "high", "risk_score": 0.9}
    elif department == "Finance" and num_pages > 100:
        return {"risk_level": "high", "risk_score": 0.85}
    return {"risk_level": "low", "risk_score": 0.2}

def get_compliance_policy(department: str) -> dict:
    policies = {
        "Legal": "All documents over 50 pages require senior review",
        "Finance": "All high-risk documents require CFO approval",
        "HR": "Standard review process applies"
    }
    return {"policy": policies.get(department, "No specific policy found")}

def create_escalation_ticket(title: str, risk_level: str, reason: str) -> dict:
    ticket_id = f"ESC-{random.randint(100, 999)}"
    return {"ticket_id": ticket_id, "status": "created", "priority": "high"}

def send_notification(recipient: str, subject: str, message: str) -> dict:
    msg_id = f"MSG-{random.randint(100, 999)}"
    return {"sent": True, "recipient": recipient, "message_id": msg_id}

# --- Tool Schemas for Groq ---

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search for documents in the knowledge base",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_document_risk",
            "description": "Assess risk of a document based on metadata",
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
            "description": "Get compliance policy for a department",
            "parameters": {"type": "object", "properties": {"department": {"type": "string"}}, "required": ["department"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_escalation_ticket",
            "description": "Create an escalation ticket for high-risk documents",
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
            "description": "Send email notification",
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

AVAILABLE_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "assess_document_risk": assess_document_risk,
    "get_compliance_policy": get_compliance_policy,
    "create_escalation_ticket": create_escalation_ticket,
    "send_notification": send_notification
}

# --- Test Execution ---

if __name__ == "__main__":
    print(search_knowledge_base("legal"))
    print(assess_document_risk("Audit", "Finance", 120))
    print(get_compliance_policy("Legal"))
    print(create_escalation_ticket("Q3 Audit", "high", "High page count"))
    print(send_notification("cfo@company.com", "Alert", "High risk doc created"))