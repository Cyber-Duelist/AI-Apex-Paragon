import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Load Environment and Initialize Client
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Define the Actual Python Functions (The Tools)
def get_document_info(document_id: str) -> dict:
    # Hardcoded data simulating a database lookup
    if document_id == "DOC-001":
        return {"title": "Merger Agreement", "department": "Legal", "num_pages": 105}
    return {"error": "Document not found"}

def calculate_risk_score(num_pages: int, department: str) -> dict:
    # Deterministic risk engine calculation
    if department.lower() == "legal" and num_pages > 100:
        return {"risk_score": 0.9, "risk_level": "high"}
    return {"risk_score": 0.2, "risk_level": "low"}

# 3. Define the Tool Schemas for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_document_info",
            "description": "Retrieves document details such as title, department, and total pages using a unique document ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The unique identifier for the document, e.g., 'DOC-001'"
                    }
                },
                "required": ["document_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_score",
            "description": "Calculates the risk score and risk level for a document based on its page count and department.",
            "parameters": {
                "type": "object",
                "properties": {
                    "num_pages": {
                        "type": "integer",
                        "description": "The total number of pages in the document."
                    },
                    "department": {
                        "type": "string",
                        "description": "The department originating the document, e.g., 'Legal', 'HR'."
                    }
                },
                "required": ["num_pages", "department"]
            }
        }
    }
]

# 4. Initialize Conversation State (Added System Prompt)
messages = [
    {
        "role": "system",
        "content": "You are an expert AI orchestrator. You must use the provided tools to fetch data and calculate risk. Always execute tools sequentially and output clean, valid tool calls."
    },
    {
        "role": "user",
        "content": "Get the document info for document ID 'DOC-001', then calculate its risk score."
    }
]

# 5. Agent Orchestration Loop
while True:
    # Make the API call with tools provided
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False
    )
    
    response_message = response.choices[0].message
    
    # Check if the model wants to call a tool
    if response_message.tool_calls:
        # Bulletproof way to append the assistant's request (prevents stringification errors)
        messages.append(response_message.model_dump(exclude_unset=True))
        
        # Process each tool call requested by the model
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"=== TOOL CALL: {function_name} ===")
            print(f"Arguments: {json.dumps(function_args)}")
            
            # Route to the correct Python function
            if function_name == "get_document_info":
                result = get_document_info(document_id=function_args.get("document_id"))
            elif function_name == "calculate_risk_score":
                result = calculate_risk_score(
                    num_pages=function_args.get("num_pages"),
                    department=function_args.get("department")
                )
            else:
                result = {"error": "Unknown tool executed"}
                
            print(f"Result: {json.dumps(result)}\n")
            
            # Send the function result back to the conversation stack
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result)
            })
            
        # Continue loop so the model can inspect tool data and decide its next move
        continue
    else:
        # No more tool calls required; this is the final response
        print("=== FINAL RESPONSE ===")
        print(response_message.content)
        break