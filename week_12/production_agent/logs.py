import os
import logging
from datetime import datetime

# Create logs directory automatically
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agent.log")

class AgentLogger:
    def __init__(self):
        self.logger = logging.getLogger("ProductionAgent")
        self.logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers on reload
        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)-5s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # File handler
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_request(self, task: str):
        self.logger.info(f"[REQUEST] Task: {task[:100]}")

    def log_tool_call(self, tool_name: str, args: dict, result: dict):
        self.logger.info(f"[TOOL] {tool_name} | Args: {args} | Result: {result}")

    def log_guardrail(self, check_type: str, passed: bool, reason: str = None):
        status = "PASSED" if passed else f"BLOCKED - {reason}"
        self.logger.info(f"[GUARDRAIL] {check_type}: {status}")

    def log_response(self, response: str, model_used: str, steps: int):
        self.logger.info(f"[RESPONSE] Model: {model_used} | Steps: {steps} | Response: {response[:80]}")

    def log_error(self, error: str):
        self.logger.error(f"[ERROR] {error}")


def get_last_logs(n: int = 20) -> list:
    """Read last N lines from the log file."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-n:]]


if __name__ == "__main__":
    logger = AgentLogger()

    logger.log_request("Analyze the Merger Agreement from Legal with 105 pages.")
    logger.log_guardrail("input_check", True)
    logger.log_guardrail("scope_check", True)
    logger.log_tool_call(
        "assess_document_risk",
        {"title": "Merger Agreement", "department": "Legal", "num_pages": 105},
        {"risk_level": "high", "risk_score": 0.9}
    )
    logger.log_tool_call(
        "create_escalation_ticket",
        {"title": "Merger Agreement", "risk_level": "high", "reason": "High risk document"},
        {"ticket_id": "ESC-123", "status": "created"}
    )
    logger.log_response(
        "The Merger Agreement has been escalated.",
        "llama-3.1-8b-instant",
        3
    )
    logger.log_error("Rate limit exceeded")

    print("\n=== LAST LOG ENTRIES ===")
    for line in get_last_logs():
        print(line)