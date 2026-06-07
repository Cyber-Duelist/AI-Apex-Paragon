import json
import os
import time
from datetime import datetime

class AgentMemory:
    def __init__(self, storage_file="week_12/production_agent/memory.json"):
        self.storage_file = storage_file
        # Working Memory
        self.session_id = f"sess_{int(time.time())}"
        self.conversation_history = []
        self.context = {}

    # --- Working Memory Methods ---
    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def update_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)

    def get_history(self):
        return self.conversation_history

    def clear(self):
        self.conversation_history = []
        self.context = {}
        self.session_id = f"sess_{int(time.time())}"

    # --- Persistent Memory Methods ---
    def _load_json(self):
        if not os.path.exists(self.storage_file):
            return {}
        with open(self.storage_file, "r") as f:
            return json.load(f)

    def remember(self, key, value):
        data = self._load_json()
        data[key] = value
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=4)

    def recall(self, key):
        data = self._load_json()
        return data.get(key)

# --- Test Flow ---
if __name__ == "__main__":
    mem = AgentMemory()

    # 1. Add 3 messages
    mem.add_message("user", "Hello")
    mem.add_message("assistant", "Hi there")
    mem.add_message("user", "What is the policy for Legal?")

    # 2. Store 2 context facts
    mem.update_context("department", "Legal")
    mem.update_context("status", "pending_review")

    # 3. Save 2 things to persistent memory
    mem.remember("total_sessions", 1)
    mem.remember("last_document", "Q3_Audit.pdf")

    print("Working memory history:", len(mem.get_history()))
    print("Context (department):", mem.get_context("department"))

    # 4. Clear working memory
    mem.clear()
    print("\n[!] Working memory cleared.")
    print("History length after clear:", len(mem.get_history()))
    print("Context after clear (department):", mem.get_context("department"))

    # 5. Recall from persistent memory
    print("\nRecalling persistent memory:")
    print("Last document:", mem.recall("last_document"))
    print("Total sessions:", mem.recall("total_sessions"))