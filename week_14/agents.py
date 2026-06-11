import os
import json
from dotenv import load_dotenv
from groq import Groq
from tools import TOOL_SCHEMAS, AVAILABLE_FUNCTIONS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use a faster model to avoid rate limits
MODEL = "llama-3.1-8b-instant"

class Agent:
    def __init__(self, role_name: str, system_prompt: str, tools=None):
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.tools = tools

    def run(self, message: str) -> str:
        print(f"\n[{self.role_name} is thinking...]")
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]

        # Retry logic for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                kwargs = {
                    "model": MODEL,
                    "messages": messages,
                    "temperature": 0.2
                }
                if self.tools:
                    kwargs["tools"] = self.tools
                    kwargs["tool_choice"] = "auto"
                    kwargs["parallel_tool_calls"] = False

                while True:
                    response = client.chat.completions.create(**kwargs)
                    msg = response.choices[0].message

                    if msg.tool_calls:
                        messages.append(msg)
                        for tool_call in msg.tool_calls:
                            fn_name = tool_call.function.name
                            fn_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                            if fn_args is None:
                                fn_args = {}
                            
                            print(f"  [{self.role_name}] 🛠️ Used tool: {fn_name}({fn_args})")
                            fn_result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": fn_name,
                                "content": str(fn_result)
                            })
                    else:
                        final_output = msg.content or "Completed."
                        print(f"[{self.role_name}] Output:\n{final_output}")
                        return final_output
                        
            except Exception as e:
                if "429" in str(e):
                    import time
                    print(f"  [Rate Limit] Waiting 5 seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(5)
                else:
                    raise e
        
        return "Agent failed due to rate limits."

# --- Agent Personas ---

diagnoser_prompt = """
You are the Diagnoser Agent in a DevOps Swarm.
A CI/CD pipeline just failed. The user will provide the error log.
Your job is to read the error log, understand why it failed, and provide a clear, concise summary of the root cause.
DO NOT write the code to fix it. Just explain the problem so the Developer Agent can fix it.
"""
diagnoser = Agent("Diagnoser", diagnoser_prompt)

developer_prompt = """
You are the Developer Agent in a DevOps Swarm.
Your job is to fix broken code. You have tools to `read_file` and `write_file`.
First, use `read_file` to inspect the code mentioned in the diagnosis.
Second, fix the logical errors in the code.
Third, use `write_file` to completely overwrite the file with the corrected code.
When you are done, explain what you changed.
"""
developer = Agent("Developer", developer_prompt, tools=[TOOL_SCHEMAS[0], TOOL_SCHEMAS[1]])

verifier_prompt = """
You are the Verifier Agent in a DevOps Swarm.
Your job is to verify that the Developer's fix actually worked.
Use the `run_tests` tool to execute pytest.
Read the output. If it says 'failed', tell the Orchestrator that the fix failed and provide the new error.
If it says 'passed', tell the Orchestrator that the fix was successful.
"""
verifier = Agent("Verifier", verifier_prompt, tools=[TOOL_SCHEMAS[2]])

pr_agent_prompt = """
You are the PR Agent. The build has been successfully fixed.
Write a professional, concise GitHub Pull Request summary explaining the root cause of the bug and how it was fixed.
"""
pr_agent = Agent("PR Agent", pr_agent_prompt)
