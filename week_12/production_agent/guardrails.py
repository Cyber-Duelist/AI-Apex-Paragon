class SecurityGuardrail:
    def check_input(self, user_input: str) -> dict:
        injections = ["ignore previous", "you are now", "pirate", "hacker"]
        for inj in injections:
            if inj in user_input.lower():
                return {"is_safe": False, "reason": "Prompt injection detected."}
        return {"is_safe": True}

    def check_tool_call(self, func_name: str, func_args: dict) -> dict:
        """Inspects arguments of tool calls to prevent data exfiltration."""
        # NEW: Strict Email Domain Validation
        if func_name == "send_notification":
            recipient = func_args.get("recipient", "")
            if "@company.com" not in recipient:
                return {"is_safe": False, "reason": f"Security violation: {recipient} is an unauthorized domain."}
        
        return {"is_safe": True}

    def check_output(self, output: str) -> dict:
        return {"is_safe": True}