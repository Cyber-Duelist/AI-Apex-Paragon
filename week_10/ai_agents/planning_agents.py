import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ==========================================
# 2. DEFINE THE TOOLS (The Python Functions)
# ==========================================
def search_documents(query: str) -> dict:
    """Mock database search returning multiple documents."""
    return {
        "documents": [
            {"title": "Merger Agreement", "department": "Legal"},
            {"title": "Non-Disclosure Agreement", "department": "Legal"},
            {"title": "Vendor Contract", "department": "Legal"}
        ]
    }

def assess_risk(title: str, department: str) -> dict:
    """Mock risk assessment algorithm."""
    return {"risk_level": "high", "risk_score": 0.9}

def generate_summary(title: str, risk_level: str, policy: str) -> dict:
    """Generates a compliance summary string."""
    return {"summary": f"Document '{title}' is {risk_level} risk. Policy: {policy} requires senior review."}

def send_report(summary: str, recipient: str) -> dict:
    """Mock email/reporting API."""
    return {"sent": True, "recipient": recipient}

available_functions = {
    "search_documents": search_documents,
    "assess_risk": assess_risk,
    "generate_summary": generate_summary,
    "send_report": send_report
}

# ==========================================
# 3. DEFINE THE TOOL SCHEMA
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Searches the database for documents matching a specific query.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assess_risk",
            "description": "Calculates the risk level for a given document.",
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
            "name": "generate_summary",
            "description": "Generates a final text summary of a document's risk profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "risk_level": {"type": "string"},
                    "policy": {"type": "string", "description": "The relevant compliance policy to mention."}
                },
                "required": ["title", "risk_level", "policy"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_report",
            "description": "Sends a generated summary report to a specified email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "recipient": {"type": "string", "description": "Email address of the recipient."}
                },
                "required": ["summary", "recipient"]
            }
        }
    }
]

# ==========================================
# 4. THE PLANNING AGENT LOOP
# ==========================================
def run_planning_agent(goal: str):
    print("=== PLANNING AGENT STARTED ===")
    print(f"Goal: {goal}\n")
    
    # Notice the strict system prompt. We tell it to process ALL items and work step-by-step.
    messages = [
        {
            "role": "system", 
            "content": "You are an autonomous planning agent. Break the user's goal into logical steps. "
                       "You must process ALL items found in searches. Do not skip any documents. "
                       "Use tools sequentially to complete the mission."
        },
        {"role": "user", "content": goal}
    ]
    
    step_counter = 1
    
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False # Forces it to execute logically, one step at a time
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                
                # Defensive arguments parsing (from our previous fix)
                raw_args = tool_call.function.arguments
                func_args = json.loads(raw_args) if raw_args and isinstance(json.loads(raw_args), dict) else {}
                
                print(f"Step {step_counter} — TOOL CALL: {func_name}")
                print(f"Arguments: {json.dumps(func_args)}")
                
                # Execute the function
                func = available_functions[func_name]
                result = func(**func_args)
                
                print(f"Result: {json.dumps(result)}\n")
                
                # Report back to the LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result),
                })
                
                step_counter += 1
        else:
            # Task is fully complete
            print("=== FINAL RESPONSE ===")
            print(response_message.content)
            break

if __name__ == "__main__":
    complex_mission = (
        "Search for all Legal documents, assess the risk of each one, "
        "generate a summary report containing all of them (use 'Standard Policy' for the policy argument), "
        "and send it to compliance@company.com."
    )
    run_planning_agent(complex_mission)