import requests
import json

messages = [
    {"role": "user", "content": "I have a 105-page document called 'Merger Agreement' from Legal. Check the policy, and escalate it with a reason."},
    {"role": "assistant", "content": None, "tool_calls": [{"id": "call_123", "type": "function", "function": {"name": "escalate_document", "arguments": "{}"}}]},
    {"role": "tool", "tool_call_id": "call_123", "name": "escalate_document", "content": '{"escalated": True}'}
]

res = requests.post("http://127.0.0.1:8000/api/stream_agent", json={"messages": messages}, stream=True)
for line in res.iter_lines():
    if line:
        print(line.decode('utf-8'))
