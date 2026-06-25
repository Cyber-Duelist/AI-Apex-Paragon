class Guardrails:
    def validate_input(self, text: str) -> dict:
        if not text.strip():
            return {"safe": False, "reason": "Input is empty"}
        if len(text) > 1000:
            return {"safe": False, "reason": "Input exceeds 1000 characters"}
        
        forbidden = ["ignore previous", "jailbreak", "bypass", "drop table", "delete all", "system prompt"]
        if any(f in text.lower() for f in forbidden):
            return {"safe": False, "reason": "Forbidden content detected"}
            
        return {"safe": True}

    def validate_scope(self, task: str) -> dict:
        allowed = ["document", "risk", "compliance", "analyze", "escalate", "report", "audit", "legal", "finance", "hr", "policy", "review"]
        if any(word in task.lower() for word in allowed):
            return {"in_scope": True}
        return {"in_scope": False, "reason": "Task outside allowed scope"}

    def validate_output(self, response: str) -> dict:
        if len(response) < 20:
            return {"valid": False, "reason": "Response too short"}
        
        refusals = ["I cannot", "I don't know", "As an AI", "I am unable"]
        if any(r in response for r in refusals):
            return {"valid": False, "reason": "Model refusal detected"}
            
        return {"valid": True}

    def check_escalation(self, risk_score: float) -> dict:
        if risk_score >= 0.7:
            return {"should_escalate": True}
        return {"should_escalate": False, "reason": "Risk score below threshold"}

# --- Test Flow ---
if __name__ == "__main__":
    g = Guardrails()

    # Testing validate_input
    print(f"Input Validation (Pass): {'PASS' if g.validate_input('Analyze this document') else 'FAIL'}")
    print(f"Input Validation (Fail): {'PASS' if not g.validate_input('jailbreak this system')['safe'] else 'FAIL'}")

    # Testing validate_scope
    print(f"Scope Validation (Pass): {'PASS' if g.validate_scope('Audit the finance report')['in_scope'] else 'FAIL'}")
    print(f"Scope Validation (Fail): {'PASS' if not g.validate_scope('Order me a pizza')['in_scope'] else 'FAIL'}")

    # Testing validate_output
    print(f"Output Validation (Pass): {'PASS' if g.validate_output('The analysis shows high risk for the legal document')['valid'] else 'FAIL'}")
    print(f"Output Validation (Fail): {'PASS' if not g.validate_output('I cannot help you')['valid'] else 'FAIL'}")

    # Testing check_escalation
    print(f"Escalation (Pass): {'PASS' if g.check_escalation(0.8)['should_escalate'] else 'FAIL'}")
    print(f"Escalation (Fail): {'PASS' if not g.check_escalation(0.5)['should_escalate'] else 'FAIL'}")