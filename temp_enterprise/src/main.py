import os
import sys
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from agent import ProductionAgent
from tools import TOOL_SCHEMAS, AVAILABLE_FUNCTIONS
from logs import AgentLogger, get_last_logs

app = FastAPI(title="Production Agent API")
agent = ProductionAgent()
logger = AgentLogger()

# Pydantic Models
class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    task: str
    response: str
    status: str
    steps_taken: int
    model_used: str

# Step counter
step_counter = {"count": 0}

def classify_query(task: str) -> str:
    """Route simple tasks to fast model, complex to smart model."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Classify this task as 'simple' or 'complex'. Reply with one word only."},
                {"role": "user", "content": task}
            ],
            max_tokens=5
        )
        classification = response.choices[0].message.content.strip().lower()
        if "simple" in classification:
            return "llama-3.1-8b-instant"
        return "llama-3.3-70b-versatile"
    except Exception:
        return "llama-3.1-8b-instant"

def tracked_process(task: str) -> tuple[str, int, str]:
    step_counter["count"] = 0

    # Guardrails
    input_check = agent.guardrails.validate_input(task)
    if not input_check.get("safe"):
        reason = input_check["reason"]
        logger.log_guardrail("input_check", False, reason)
        return f"[SECURITY BLOCK] {reason}", 0, "none"

    logger.log_guardrail("input_check", True)

    scope_check = agent.guardrails.validate_scope(task)
    if not scope_check.get("in_scope"):
        reason = scope_check["reason"]
        logger.log_guardrail("scope_check", False, reason)
        return f"[OUT OF SCOPE] {reason}", 0, "none"

    logger.log_guardrail("scope_check", True)
    logger.log_request(task)

    # Route to correct model
    selected_model = classify_query(task)
    print(f"  Routing to: {selected_model}")

    agent.memory.add_message("user", task)

    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": task}
    ]

    try:
        while True:
            response = agent.client.chat.completions.create(
                model=selected_model,
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
                    print(f"  TOOL CALL: {fn_name}")
                    logger.log_tool_call(fn_name, fn_args, fn_result)
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

    except Exception as e:
        logger.log_error(str(e))
        return f"[ERROR] {str(e)}", step_counter["count"], selected_model

    output_check = agent.guardrails.validate_output(final_answer)
    if not output_check.get("valid"):
        reason = output_check["reason"]
        return f"[OUTPUT INVALID] {reason}", step_counter["count"], selected_model

    logger.log_response(final_answer, selected_model, step_counter["count"])
    agent.memory.add_message("assistant", final_answer)
    return final_answer, step_counter["count"], selected_model


# Endpoints
@app.get("/")
def root():
    return {"status": "Production Agent API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "model": agent.model}

@app.post("/run", response_model=TaskResponse)
def run_task(req: TaskRequest):
    response, steps, model_used = tracked_process(req.task)

    if response.startswith("[SECURITY BLOCK]") or response.startswith("[OUT OF SCOPE]"):
        status = "blocked"
    elif response.startswith("[ERROR]"):
        status = "error"
    else:
        status = "completed"

    return TaskResponse(
        task=req.task,
        response=response,
        status=status,
        steps_taken=steps,
        model_used=model_used
    )

@app.get("/memory")
def get_memory():
    return {
        "history_length": len(agent.memory.get_history()),
        "context": agent.memory.context,
        "session_id": agent.memory.session_id
    }

@app.get("/logs")
def get_logs():
    return {"logs": get_last_logs(20)}