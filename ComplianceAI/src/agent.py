import os
import json
from groq import Groq
from tools import TOOL_SCHEMAS, AVAILABLE_FUNCTIONS
from memory import AgentMemory
from guardrails import Guardrails

def get_available_model():
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    preferred_models = ['llama-3.1-8b-instant', 'llama-3.3-70b-versatile', 'gemma2-9b-it']
    for model in preferred_models:
        try:
            client.chat.completions.create(model=model, messages=[{'role': 'user', 'content': 'hi'}], max_tokens=1)
            return model
        except Exception:
            continue
    raise Exception('No available models found.')

class ComplianceAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.memory = AgentMemory()
        self.guardrails = Guardrails()
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = get_available_model()
        self.system_prompt = (
            'You are ComplianceAI, an expert compliance analysis agent. '
            'You help users analyze their documents against regulatory frameworks (GDPR, SOX, HIPAA). '
            'You can search documents, run compliance analyses, create escalation tickets, and send notifications. '
            'Use the available tools to complete tasks. Be thorough, professional, and actionable. '
            'Always explain your findings clearly.'
        )

    def process_request(self, task: str) -> str:
        # 1. Input guardrails
        input_check = self.guardrails.validate_input(task)
        if not input_check.get('safe'):
            return f"🚫 **Security Block:** {input_check['reason']}"

        # 2. Scope guardrails
        scope_check = self.guardrails.validate_scope(task)
        if not scope_check.get('in_scope'):
            return f"ℹ️ {scope_check['reason']}"

        # 3. Add to memory
        self.memory.add_message('user', task)

        # 4. Agent loop
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': task}
        ]

        max_iterations = 10
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice='auto',
                parallel_tool_calls=False
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    fn_args = json.loads(raw_args) if raw_args else {}
                    
                    # Inject user_id for tools that need it
                    if fn_name in ['search_documents', 'analyze_compliance', 'get_risk_summary', 'create_ticket']:
                        fn_args['user_id'] = self.user_id
                    
                    fn_result = AVAILABLE_FUNCTIONS[fn_name](**fn_args)
                    self.memory.update_context(fn_name, fn_result)
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'name': fn_name,
                        'content': json.dumps(fn_result)
                    })
            else:
                final_answer = msg.content or 'Task completed.'
                break
        else:
            final_answer = 'Maximum tool iterations reached. Please try a more specific request.'

        # 5. Output validation
        output_check = self.guardrails.validate_output(final_answer)
        if not output_check.get('valid'):
            return f"⚠️ {output_check['reason']}"

        # 6. Save to memory
        self.memory.add_message('assistant', final_answer)
        return final_answer
