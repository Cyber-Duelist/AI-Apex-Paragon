import os
import json
from dotenv import load_dotenv
from groq import Groq

# Import the modules you built in Packs 1, 2, and 3
from tools import AVAILABLE_FUNCTIONS, TOOL_SCHEMAS
from memory import AgentMemory
from guardrails import SecurityGuardrail

load_dotenv()

class ProductionAgent:
    """
    The central intelligence that wires together Memory, Tools, and Guardrails
    into a continuous, safe, autonomous loop.
    """
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # 🔴 NEW: Dynamic Model Selection
        self.model = self._get_best_available_model()
        print(f"[*] Agent initialized. Dynamically selected model: {self.model}\n")
        
        self.memory = AgentMemory()
        self.guardrails = SecurityGuardrail()
        
        self.system_prompt = (
            "You are an enterprise compliance agent. "
            "Search the knowledge base before assessing risk. "
            "You must follow department policies and escalate high-risk documents."
        )

    def _get_best_available_model(self) -> str:
        """
        Queries the Groq API for currently active models and selects the best 
        available option based on our priority tier.
        """
        try:
            # Our wishlist: ranked from best tool-use model down to standard fallbacks
            preferred_models = [
                "llama3-groq-70b-8192-tool-use-preview", # Often the active name for tool-use
                "llama-3.3-70b-versatile",               # The new powerhouse
                "llama-3.1-70b-versatile",               # Reliable fallback
                "llama3-70b-8192"                        # Ultimate fallback
            ]
            
            # Ask Groq what models are actually online right now
            active_models = [m.id for m in self.client.models.list().data]
            
            # Return the highest priority model that is actually online
            for model in preferred_models:
                if model in active_models:
                    return model
                    
            # Absolute fallback if the API list fails to match anything
            return "llama-3.3-70b-versatile"
            
        except Exception as e:
            print(f"Warning: Could not fetch active model list. Defaulting. Error: {e}")
            return "llama-3.3-70b-versatile"

    def process_request(self, user_input: str) -> str:
        # ==========================================
        # 1. INPUT GUARDRAIL
        # ==========================================
        input_check = self.guardrails.check_input(user_input)
        if not input_check["is_safe"]:
            return f"[SECURITY BLOCK] {input_check['reason']}"

        # ==========================================
        # 2. MEMORY LOAD
        # ==========================================
        self.memory.clear_working_memory()
        self.memory.add_message("user", user_input)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory.get_conversation_history())

        print("=== AGENT EXECUTING ===")
        
        # ==========================================
        # 3. THE REACT LOOP
        # ==========================================
        step_count = 0
        max_steps = 10 
        
        while step_count < max_steps:
            step_count += 1
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                parallel_tool_calls=False
            )
            
            msg = response.choices[0].message
            
            # ==========================================
            # 4. OUTPUT GUARDRAIL
            # ==========================================
            if msg.content:
                out_check = self.guardrails.check_output(msg.content)
                if not out_check["is_safe"]:
                    return f"[SECURITY BLOCK] {out_check['reason']}"

            # ==========================================
            # 5. TOOL EXECUTION & VALIDATION
            # ==========================================
            if msg.tool_calls:
                messages.append(msg)
                
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    
                    raw_args = tool_call.function.arguments
                    func_args = json.loads(raw_args) if raw_args and isinstance(json.loads(raw_args), dict) else {}
                    
                    print(f"-> Tool Call: {func_name} | Args: {func_args}")
                    
                    tool_check = self.guardrails.check_tool_call(func_name, func_args)
                    
                    if not tool_check["is_safe"]:
                        print(f"   ❌ [BLOCKED] {tool_check['reason']}")
                        result_str = f"ERROR: Execution blocked by security policy - {tool_check['reason']}"
                    else:
                        print(f"   ✅ [AUTHORIZED]")
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
                # ==========================================
                # 6. FINAL ANSWER
                # ==========================================
                final_answer = msg.content
                self.memory.add_message("assistant", final_answer)
                self.memory.save_session_summary()
                return final_answer
                
        return "[SYSTEM ERROR] Agent hit maximum iteration limit without resolving."

# ==========================================
# TEST BLOCK
# ==========================================
if __name__ == "__main__":
    agent = ProductionAgent()
    print("=== INITIALIZING PRODUCTION AGENT ===\n")
    
    task = (
        "Search for the Merger Agreement. Assess its risk. "
        "Check the legal compliance policy. "
        "If it's high risk, create an escalation ticket with a good reason, "
        "and send a notification to compliance@company.com."
    )
    
    print(f"User Request: {task}\n")
    final_response = agent.process_request(task)
    
    print("\n=== FINAL RESPONSE ===")
    print(final_response)