import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ==========================================
# 2. DEFINE THE TOOLS (The Python Functions)
# ==========================================

def get_document_risk(title: str, department: str, num_pages: int) -> dict:
    """Mock database lookup for document risk."""
    return {"risk_level": "high", "risk_score": 0.9}

def get_department_policy(department: str) -> dict:
    """Mock database lookup for department compliance policies."""
    policies = {
        "Legal": "All documents over 50 pages require senior review",
        "Finance": "All high-risk documents require CFO approval",
        "HR": "Standard review process applies"
    }
    return {"policy": policies.get(department, "No specific policy found.")}

def escalate_document(title: str, reason: str) -> dict:
    """Mock API call to a ticketing system (like Jira or ServiceNow)."""
    return {"escalated": True, "ticket_id": "ESC-001", "reason": reason}

# Map string names to the actual Python functions so our loop can call them
available_functions = {
    "get_document_risk": get_document_risk,
    "get_department_policy": get_department_policy,
    "escalate_document": escalate_document,
}

# ==========================================
# 3. DEFINE THE TOOL SCHEMA (The Menu)
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_document_risk",
            "description": "Calculates the risk level of a document based on its metadata.",
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
            "name": "get_department_policy",
            "description": "Retrieves the standard operating policy for a specific department.",
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
            "name": "escalate_document",
            "description": "Escalates a document to management by creating a high-priority ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "reason": {"type": "string", "description": "Detailed reason for escalation."}
                },
                "required": ["title", "reason"]
            }
        }
    }
]

# ==========================================
# 4. THE AGENT LOOP (Reason -> Act -> Observe)
# ==========================================
def run_agent(user_prompt: str):
    print("=== INITIALIZING AGENT ===")
    print(f"Task: {user_prompt}\n")
    
    # The agent's memory. It must remember everything it has done.
    messages = [{"role": "user", "content": user_prompt}]
    
    # The infinite loop that keeps the agent alive until the job is done
    while True:
        # Step A: The Agent Thinks
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False # Force it to do one thing at a time
        )
        
        response_message = response.choices[0].message
        
        # Step B: Does the Agent want to use a tool?
        if response_message.tool_calls:
            # We must append the Agent's tool request to memory so it remembers asking for it
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                # Convert the JSON string from the LLM into a Python Dictionary
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"=== TOOL CALL: {function_name} ===")
                
                # Dynamically call our Python function using the dictionary map
                function_to_call = available_functions[function_name]
                function_result = function_to_call(**function_args) # Unpack dictionary into kwargs
                
                print(f"Result: {json.dumps(function_result)}")
                
                # Step C: The Agent Observes
                # Send the result BACK to the LLM by appending it as a "tool" role message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result),
                })
                
        else:
            # Step D: The Task is Complete
            # If the LLM doesn't request a tool, it means it has enough info to give a final answer
            print("\n=== FINAL RESPONSE ===")
            print(response_message.content)
            break

if __name__ == "__main__":
    task = (
        "Analyze the document 'Merger Agreement' from Legal department with 105 pages. "
        "Check the department policy and if the document is high risk, escalate it with a reason."
    )
    run_agent(task)