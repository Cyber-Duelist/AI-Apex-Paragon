class Guardrails:
    def validate_input(self, text):
        if not text.strip():
            return {'safe': False, 'reason': 'Input is empty'}
        if len(text) > 2000:
            return {'safe': False, 'reason': 'Input exceeds 2000 characters'}
        forbidden = ['ignore previous', 'jailbreak', 'bypass', 'drop table', 'delete all', 'system prompt', 'reveal your', 'pretend you']
        if any(f in text.lower() for f in forbidden):
            return {'safe': False, 'reason': 'Potential prompt injection detected'}
        return {'safe': True}

    def validate_scope(self, task):
        allowed = ['document', 'risk', 'compliance', 'analyze', 'escalate', 'report', 'audit', 'legal', 'finance', 'hr', 'policy', 'review', 'gdpr', 'sox', 'hipaa', 'regulation', 'search', 'find', 'check', 'assess', 'upload', 'help', 'what', 'how', 'show', 'list', 'tell', 'explain', 'summary', 'generate']
        if any(word in task.lower() for word in allowed):
            return {'in_scope': True}
        return {'in_scope': False, 'reason': 'Please ask about document compliance, risk analysis, or use one of the available tools.'}

    def validate_output(self, response):
        if len(response) < 10:
            return {'valid': False, 'reason': 'Response too short'}
        return {'valid': True}
