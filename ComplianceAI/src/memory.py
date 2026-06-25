import time

class AgentMemory:
    def __init__(self):
        self.session_id = f'sess_{int(time.time())}'
        self.conversation_history = []
        self.context = {}

    def add_message(self, role, content):
        self.conversation_history.append({'role': role, 'content': content})

    def update_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)

    def get_history(self):
        return self.conversation_history

    def clear(self):
        self.conversation_history = []
        self.context = {}
        self.session_id = f'sess_{int(time.time())}'
