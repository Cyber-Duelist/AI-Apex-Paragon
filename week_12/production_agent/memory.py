import os
import json
import datetime

class AgentMemory:
    """
    Dual-memory architecture for production agents.
    Working Memory: Session-specific, resets between runs.
    Persistent Memory: Survives restarts via JSON storage.
    """
    
    def __init__(self, persist_file="memory.json"):
        # Setup file path relative to this script
        self.persist_path = os.path.join(os.path.dirname(__file__), persist_file)
        
        # Initialize Persistent Memory
        self.persistent_data = {}
        self._load_persistent()
        
        # Initialize Working Memory
        self.clear_working_memory()

    def _load_persistent(self):
        """Loads data from the JSON file or initializes defaults if it doesn't exist."""
        if os.path.exists(self.persist_path):
            with open(self.persist_path, 'r') as f:
                self.persistent_data = json.load(f)
        else:
            self.persistent_data = {
                "total_sessions": 0,
                "documents_analyzed": 0,
                "escalations_created": 0,
                "last_active": None
            }
            self._save_persistent()

    def _save_persistent(self):
        """Saves current persistent_data dictionary to the JSON file."""
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        with open(self.persist_path, 'w') as f:
            json.dump(self.persistent_data, f, indent=4)

    # ==========================================
    # WORKING MEMORY METHODS (In-Memory)
    # ==========================================
    def add_message(self, role: str, content: str):
        """Appends a message to the active context window."""
        self.conversation_history.append({"role": role, "content": content})

    def update_context(self, key: str, value: any):
        """Stores a fact in the current working session."""
        self.context[key] = value

    def get_context(self, key: str) -> any:
        """Retrieves a fact from the current working session."""
        return self.context.get(key)
        
    def get_conversation_history(self) -> list:
        """Returns the full conversation history for the LLM."""
        return self.conversation_history

    def clear_working_memory(self):
        """Resets working memory for a new session/task."""
        self.conversation_history = []
        self.context = {}
        self.current_session = {
            "session_id": f"sess_{int(datetime.datetime.now().timestamp())}",
            "start_time": datetime.datetime.now().isoformat(),
            "tasks_completed": 0
        }

    # ==========================================
    # PERSISTENT MEMORY METHODS (JSON File)
    # ==========================================
    def remember(self, key: str, value: any):
        """Saves a key-value pair to persistent hard drive storage."""
        self.persistent_data[key] = value
        self._save_persistent()

    def recall(self, key: str) -> any:
        """Retrieves a value from persistent hard drive storage."""
        return self.persistent_data.get(key)

    def save_session_summary(self):
        """Updates and saves overarching system statistics."""
        self.persistent_data["total_sessions"] = self.persistent_data.get("total_sessions", 0) + 1
        self.persistent_data["last_active"] = datetime.datetime.now().isoformat()
        self._save_persistent()


# ==========================================
# TEST BLOCK
# ==========================================
if __name__ == "__main__":
    print("=== TESTING AGENT MEMORY ===")
    
    # 1. Create memory instance
    mem = AgentMemory()
    
    # 2. Add 3 messages
    mem.add_message("system", "You are a helpful compliance agent.")
    mem.add_message("user", "Analyze the Merger Agreement.")
    mem.add_message("assistant", "I am analyzing the document now.")
    print(f"Added {len(mem.get_conversation_history())} messages to conversation history")
    
    # 3. Store 2 context facts
    mem.update_context("document", "Merger Agreement")
    mem.update_context("risk_level", "high")
    print(f"Context stored: {mem.context}")
    
    print("\n=== PERSISTENT MEMORY ===")
    
    # 4. Save to persistent memory
    mem.save_session_summary() 
    mem.remember("last_document", "Merger Agreement")
    
    print(f"Saved: total_sessions = {mem.recall('total_sessions')}")
    print(f"Saved: last_document = {mem.recall('last_document')}")
    
    print("\n=== AFTER CLEAR ===")
    
    # 5. Clear working memory
    mem.clear_working_memory()
    print(f"Working memory cleared. History length: {len(mem.get_conversation_history())}")
    
    # 6. Recall from persistent memory to prove it survived the wipe
    surviving_doc = mem.recall("last_document")
    print(f"Persistent memory survived: last_document = {surviving_doc}")