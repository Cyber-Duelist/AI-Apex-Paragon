import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agent import ProductionAgent

app = FastAPI(title="Production Agent API")
agent = ProductionAgent()

# Pydantic Models
class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    task: str
    response: str
    status: str
    steps_taken: int

# Track steps globally
step_counter = {"count": 0}
original_process = agent.process_request

def tracked_process(task: str) -> str:
    step_counter["count"] = 0
    original_fn = agent.process_request

    # Patch tool call to count steps
    import json
    from tools import TOOL_SCHEMAS, AVAILABLE_FUNCTIONS
    from groq import Groq

    input_check = agent.guardrails.validate_input(task)
    if not input_check.get("safe"):
        return f"[SECURITY BLOCK] {input_check['reason']}"

    scope_check = agent.guardrails.validate_scope(task)
    if not scope_check.get("in_scope"):
        return f"[OUT OF SCOPE] {scope_check['reason']}"

    agent.memory.add_message("user", task)

    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": task}
    ]

    while True:
        response = agent.client.chat.completions.create(
            model=agent.model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            parallel_tool_calls=False
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                raw_args = tool_call.function.arguments
                fn_args = json.loads(raw_args) if raw_args else {}
                fn_result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                step_counter["count"] += 1
                agent.memory.update_context(fn_name, fn_result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": json.dumps(fn_result)
                })
        else:
            final_answer = msg.content or "Task completed via tools."
            break

    output_check = agent.guardrails.validate_output(final_answer)
    if not output_check.get("valid"):
        return f"[OUTPUT INVALID] {output_check['reason']}"

    agent.memory.add_message("assistant", final_answer)
    return final_answer


# Endpoints
@app.get("/")
def root():
    return {"status": "Production Agent API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "model": agent.model}

@app.post("/run", response_model=TaskResponse)
def run_task(req: TaskRequest):
    response = tracked_process(req.task)

    if response.startswith("[SECURITY BLOCK]") or response.startswith("[OUT OF SCOPE]"):
        status = "blocked"
    else:
        status = "completed"

    return TaskResponse(
        task=req.task,
        response=response,
        status=status,
        steps_taken=step_counter["count"]
    )

@app.get("/memory")
def get_memory():
    return {
        "history_length": len(agent.memory.get_history()),
        "context": agent.memory.context,
        "session_id": agent.memory.session_id
    }