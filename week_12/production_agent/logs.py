import json
import os
import uuid
from datetime import datetime

class AuditLogger:
    """
    Production-grade structured logger for the Enterprise Compliance Agent.
    Writes telemetry data to a JSON-Lines (.jsonl) file.
    """
    def __init__(self, log_folder_name="logs"):
        # 1. Get the absolute path to the 'production_agent' directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Define the exact path to the new 'logs' folder
        self.log_dir = os.path.join(current_dir, log_folder_name)
        
        # 3. Force the OS to create the folder
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 4. Define the file path
        self.log_file = os.path.join(self.log_dir, "telemetry.jsonl")
        
        # Print a confirmation to the terminal so we know it worked!
        print(f"[*] Telemetry Logger active. File path: {self.log_file}")

    def log_trace(self, user_id: str, query: str, status: str, response: str, duration_ms: int):
        """Appends a single structured trace to the log file."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "query": query,
            "status": status,
            "duration_ms": duration_ms,
            "response_preview": response[:100] + "..." if len(response) > 100 else response
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
# Instantiate a global logger for the app to use
system_logger = AuditLogger()