import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def get_available_model():
    """Automatically selects the best available Groq model."""
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile", 
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
    
    for model in preferred_models:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            print(f"Using model: {model}")
            return model
        except Exception:
            continue
    
    raise Exception("No available models found. Check your Groq API key.")

MODEL = get_available_model()

# ==========================================
# 2. DEFINE THE TOOLS
# ==========================================
def assess_risk(title: str, department: str) -> dict:
    """Mock risk assessment returning high risk."""
    return {"risk_level": "high", "risk_score": 0.9}

def request_human_approval(action: str, reason: str) -> dict:
    """
    PAUSES THE AGENT: The agent cannot proceed until the human types 'yes' or 'no'
    in the terminal.
    """
    print(f"\n[⚠️ HUMAN APPROVAL REQUIRED]")
    print(f"Action: {action}")
    print(f"Reason: {reason}")
    
    # This halts the Python script and waits for the user's keyboard
    user_input = input("Approve this action? (yes/no): ").strip().lower()
    
    if user_input in ['yes', 'y']:
        return {"approved": True}
    else:
        return {"approved": False, "reason": "Human rejected"}

def escalate_document(title: str, reason: str) -> dict:
    """Creates the ticket. Only runs if the human said yes."""
    return {"escalated": True, "ticket_id": "ESC-002"}

available_functions = {
    "assess_risk": assess_risk,
    "request_human_approval": request_human_approval,
    "escalate_document": escalate_document
}

# ==========================================
# 3. DEFINE THE TOOL SCHEMA
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "assess_risk",
            "description": "Calculates the risk level of a document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "department": {"type": "string"}
                },
                "required": ["title", "department"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_human_approval",
            "description": "Requests explicit human approval before taking a sensitive action. Must be called before escalating.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "The specific action needing approval (e.g., 'Escalate Document')."},
                    "reason": {"type": "string", "description": "Why this action is being taken based on prior steps."}
                },
                "required": ["action", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_document",
            "description": "Escalates a document by creating a ticket. MUST only be called if request_human_approval returned true.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["title", "reason"]
            }
        }
    }
]

# ==========================================
# 4. THE AGENT LOOP
# ==========================================
def run_agent(task: str):
    print("=== AGENT STARTED ===")
    print(f"Task: {task}\n")
    
    # We explicitly tell the system prompt about the approval rule
    messages = [
        {"role": "system", "content": "You are a secure compliance agent. You MUST call only ONE tool at a time. Wait for each tool result before calling the next tool. Never call multiple tools in one response. Work step-by-step: first assess_risk, then request_human_approval, then escalate_document if approved."},
        {"role": "user", "content": task}
    ]
    
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                
                # Defensive parsing
                raw_args = tool_call.function.arguments
                func_args = json.loads(raw_args) if raw_args and isinstance(json.loads(raw_args), dict) else {}
                
                print(f"=== TOOL CALL: {func_name} ===")
                
                func = available_functions[func_name]
                result = func(**func_args)
                
                print(f"Result: {json.dumps(result)}\n")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result),
                })
        else:
            print("=== FINAL RESPONSE ===")
            print(response_message.content)
            break

if __name__ == "__main__":
    task = (
        "Assess the risk of 'Acquisition Contract' from Legal with 200 pages. "
        "If high risk, request human approval before escalating. "
        "Only escalate if approved."
    )
    run_agent(task)