import os
import json
import PyPDF2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Priority list of models to try. If one fails (e.g. rate limit, bad json), it falls back to the next.
MODELS = [
    "llama-3.3-70b-versatile",               # High quality fallback
    "llama-3.1-8b-instant"                   # Ultra-fast lightweight fallback
]

# System prompt that defines the Agent's identity
SYSTEM_PROMPT = """You are a highly capable General Purpose Desktop AI Assistant.
You live on the user's local machine. You have tools to:
1. Search the web (Wikipedia) for general knowledge.
2. Read files they upload to you.
3. List directories on their computer.
4. Save files to their computer (e.g. generating code, writing summaries, etc.).
5. Escalate documents.

When the user asks you a question, think step by step. If you need information, use your tools. 
If they ask you to write or save a file, use the save_file tool! Format your final responses beautifully in Markdown."""

# ==========================================
# 1. DEFINE THE TOOLS (Python Functions)
# ==========================================

def search_web(query: str) -> dict:
    """A simple wikipedia search for general knowledge"""
    import urllib.request
    import urllib.parse
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            results = [f"{item['title']}: {item['snippet']}" for item in data['query']['search'][:3]]
            return {"results": results}
    except Exception as e:
        return {"error": str(e)}

def list_local_files(directory: str) -> dict:
    """Lists files in a given directory"""
    try:
        if directory == "." or directory == "":
            directory = os.getcwd()
        files = os.listdir(directory)
        return {"files": files, "directory": directory}
    except Exception as e:
        return {"error": str(e)}

def save_file(filename: str, content: str) -> dict:
    """Saves text content to a local file"""
    try:
        # Save to the local uploads directory to be safe
        safe_path = os.path.join(os.path.dirname(__file__), "uploads", filename)
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"File {filename} saved successfully at {safe_path}."}
    except Exception as e:
        return {"error": str(e)}

def read_uploaded_document(filename: str) -> dict:
    """Reads a document from the local uploads folder."""
    file_path = os.path.join(os.path.dirname(__file__), "uploads", filename)
    if not os.path.exists(file_path):
        return {"error": f"File {filename} not found in uploads directory."}
    
    try:
        ext = filename.lower().split('.')[-1]
        
        if ext == 'pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return {"content": text[:8000]}
            
        elif ext in ['txt', 'md', 'csv']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content[:8000]}
            
        else:
            return {"error": f"Unsupported file type: {ext}"}
            
    except Exception as e:
        return {"error": str(e)}

def escalate_document(title: str, reason: str) -> dict:
    """Escalates a document to senior management."""
    return {"escalated": True, "ticket_id": "REQ-999", "message": f"Escalated {title} because: {reason}"}

# ==========================================
# 2. MAP TOOLS FOR THE AGENT LOOP
# ==========================================
available_functions = {
    "search_web": search_web,
    "list_local_files": list_local_files,
    "save_file": save_file,
    "read_uploaded_document": read_uploaded_document,
    "escalate_document": escalate_document,
}

DANGEROUS_TOOLS = {"save_file", "escalate_document"}

def execute_tool_manually(tool_name: str, args: dict) -> dict:
    func = available_functions.get(tool_name)
    if not func:
        return {"error": f"Tool {tool_name} not found"}
    try:
        return func(**args)
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 3. DEFINE THE TOOL SCHEMA (The Menu)
# ==========================================
tool_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches Wikipedia for knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_local_files",
            "description": "Lists the files in a specific directory on the user's computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "The directory path, or '.' for current directory"}
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_file",
            "description": "Saves content to a local file on the user's computer. USE THIS to write reports, summaries, or code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file to save (e.g. summary.md)"},
                    "content": {"type": "string", "description": "The complete text content to write to the file"}
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_uploaded_document",
            "description": "Reads the text content of a file that the user has uploaded to the dashboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "The name of the file."}
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_document",
            "description": "Escalates a document to senior management. ALWAYS USE THIS if the user explicitly asks to escalate something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The document title"},
                    "reason": {"type": "string", "description": "Why it needs escalation"}
                },
                "required": ["title", "reason"],
            },
        },
    }
]

# ==========================================
# 4. THE AUTONOMOUS LOOP WITH STREAMING
# ==========================================

def stream_agent(messages: list):
    """
    Generator function that streams out exactly what the agent is doing at each step.
    Receives standard OpenAI-formatted messages array.
    """
    # If the messages array doesn't have a system prompt yet, inject it.
    if len(messages) > 0 and messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    while True:
        yield {"type": "think", "content": "Thinking..."}
        
        response = None
        for current_model in MODELS:
            try:
                cleaned_messages = []
                for msg in messages:
                    if hasattr(msg, "model_dump"):
                        msg = msg.model_dump(exclude_none=True)
                    if isinstance(msg, dict):
                        clean_msg = {k: v for k, v in msg.items() if k in ["role", "content", "tool_calls", "tool_call_id", "name"] and v is not None}
                        if msg.get("role") == "assistant" and "content" not in clean_msg:
                            clean_msg["content"] = None
                        cleaned_messages.append(clean_msg)
                    else:
                        cleaned_messages.append(msg)

                response = client.chat.completions.create(
                    model=current_model,
                    messages=cleaned_messages,
                    tools=tool_schema,
                    tool_choice="auto",
                    temperature=0.1
                )
                break 
            except Exception as e:
                print(f"Model {current_model} failed with error: {str(e)}")
                # Fail over silently without alarming the user
                continue 
                
        if not response:
            yield {"type": "error", "content": "CRITICAL: All models failed to process the request. Aborting."}
            break

        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name in DANGEROUS_TOOLS:
                    yield {
                        "type": "require_approval",
                        "tool": function_name,
                        "args": function_args,
                        "tool_call_id": tool_call.id,
                        "messages": messages
                    }
                    return
                
                yield {"type": "tool_call", "tool": function_name, "args": function_args}
                
                function_result = execute_tool_manually(function_name, function_args)
                
                yield {"type": "observation", "content": function_result}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result),
                })
        else:
            final_content = response_message.content
            messages.append({"role": "assistant", "content": final_content})
            yield {"type": "final_answer", "content": final_content, "messages": messages}
            break