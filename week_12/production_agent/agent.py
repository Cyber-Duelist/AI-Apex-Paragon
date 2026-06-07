import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

from tools import AVAILABLE_FUNCTIONS, TOOL_SCHEMAS
from memory import AgentMemory
from guardrails import SecurityGuardrail

load_dotenv()

class ProductionAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.memory = AgentMemory()
        self.guardrails = SecurityGuardrail()
        
        # IMPROVED: Explicitly forces multi-step chaining
        self.system_prompt = (
            "You are an enterprise compliance auditor. "
            "1. ALWAYS chain actions: If search returns document data, IMMEDIATELY call assess_document_risk. "
            "2. IF high risk, IMMEDIATELY call create_escalation_ticket and send_notification. "
            "3. DO NOT stop after one tool call if the task requires more steps. "
            "4. Output valid JSON tool calls. DO NOT use manual <function> tags."
        )

    def process_request(self, user_input: str) -> str:
        input_check = self.guardrails.check_input(user_input)
        if not input_check["is_safe"]:
            return f"[SECURITY BLOCK] {input_check['reason']}"

        self.memory.clear_working_memory()
        self.memory.add_message("user", user_input)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_conversation_history())

        # Increased step count to allow for full chaining (Search -> Assess -> Ticket -> Notify)
        for _ in range(15): 
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto"
                )
            except Exception as e:
                print(f"   ⚠️ [API ERROR] {str(e)}")
                time.sleep(2)
                continue
            
            msg = response.choices[0].message
            
            # Stop leakage
            if msg.content and ("<function" in msg.content):
                messages.append({"role": "user", "content": "Error: Use API tool calls, not manual tags."})
                continue

            if msg.tool_calls:
                messages.append(msg)
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    # Guardrail inspection of the specific call
                    tool_check = self.guardrails.check_tool_call(func_name, func_args)
                    if not tool_check["is_safe"]:
                        result_str = f"ERROR: {tool_check['reason']}"
                    else:
                        func = AVAILABLE_FUNCTIONS.get(func_name)
                        result = func(**func_args)
                        result_str = json.dumps(result)
                            
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result_str
                    })
            else:
                self.memory.add_message("assistant", msg.content)
                return msg.content
                
        return "Agent exhausted iterations (chaining failed)."