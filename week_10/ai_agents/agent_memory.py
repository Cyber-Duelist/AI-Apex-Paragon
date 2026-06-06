import os
import json
from dotenv import load_dotenv
from groq import Groq

# 1. Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ==========================================
# 2. DEFINE LONG-TERM MEMORY (The Global State)
# ==========================================
long_term_memory = {
    "user_name": "Adarsh",
    "department": "Legal",
    "last_document": None
}

# ==========================================
# 3. DEFINE THE TOOLS (Memory Functions)
# ==========================================
def remember_document(title: str, risk_level: str) -> dict:
    """Saves a document's metadata to the global long-term memory."""
    long_term_memory["last_document"] = {"title": title, "risk_level": risk_level}
    return {"remembered": True}

def get_last_document() -> dict:
    """Retrieves the last document from global long-term memory."""
    return long_term_memory["last_document"] if long_term_memory["last_document"] else {"error": "No document found"}

available_functions = {
    "remember_document": remember_document,
    "get_last_document": get_last_document,
}

# ==========================================
# 4. DEFINE THE TOOL SCHEMA (The Menu)
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "remember_document",
            "description": "Saves a document's title and risk level into long-term memory for later retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "risk_level": {"type": "string"}
                },
                "required": ["title", "risk_level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_last_document",
            "description": "Retrieves the details of the last document the user asked about.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# ==========================================
# 5. INITIALIZE SHORT-TERM MEMORY
# ==========================================
short_term_memory = [
    {"role": "system", "content": "You are a helpful AI assistant. Use tools to remember and recall facts."}
]

# ==========================================
# 6. THE AGENT LOOP
# ==========================================
def run_task(task_number: int, user_prompt: str):
    print(f"=== TASK {task_number} ===")
    
    short_term_memory.append({"role": "user", "content": user_prompt})
    
    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=short_term_memory,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            short_term_memory.append(response_message)
            
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                
                # =========================================================
                # THE FIX: Defensive Parsing for Empty Arguments
                # =========================================================
                raw_args = tool_call.function.arguments
                if not raw_args:
                    func_args = {}
                else:
                    func_args = json.loads(raw_args)
                    if not isinstance(func_args, dict): # Catches "null"
                        func_args = {}
                # =========================================================
                
                print(f"=== TOOL CALL: {func_name} ===")
                
                func = available_functions[func_name]
                result = func(**func_args)
                
                print(f"Result: {json.dumps(result)}")
                
                short_term_memory.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(result),
                })
        else:
            short_term_memory.append({"role": "assistant", "content": response_message.content})
            
            print(f"Short-term memory size: {len(short_term_memory)} messages")
            print(f"Long-term memory: {json.dumps(long_term_memory)}")
            print(f"=== FINAL RESPONSE ===")
            print(response_message.content)
            print("-" * 50 + "\n")
            break

if __name__ == "__main__":
    # Task 1 writes to memory
    run_task(1, "Analyze the Merger Agreement, it is high risk. Remember it.")
    
    # Task 2 reads from memory
    run_task(2, "What was the last document I asked you about?")