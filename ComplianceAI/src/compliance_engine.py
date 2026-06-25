import os
import json
from groq import Groq

FRAMEWORK_PROMPTS = {
    'GDPR': (
        'You are a GDPR compliance expert. Analyze the following document text for GDPR compliance issues.\n'
        'Check for: personal data handling, consent mechanisms, data retention policies, '
        'right to erasure provisions, data breach notification procedures, cross-border data transfers, '
        'privacy by design principles.\n'
        'Return your analysis as a JSON object with these exact keys:\n'
        '- risk_score: float 0.0 to 1.0\n'
        '- risk_level: "low" or "medium" or "high"\n'
        '- findings: list of strings (specific issues found)\n'
        '- recommendations: list of strings (suggested actions)\n'
        'Return ONLY valid JSON, no markdown or explanation.'
    ),
    'SOX': (
        'You are a SOX (Sarbanes-Oxley) compliance expert. Analyze the following document text for SOX compliance issues.\n'
        'Check for: financial reporting accuracy, internal controls, audit trail completeness, '
        'management accountability, whistleblower protections, record retention.\n'
        'Return your analysis as a JSON object with these exact keys:\n'
        '- risk_score: float 0.0 to 1.0\n'
        '- risk_level: "low" or "medium" or "high"\n'
        '- findings: list of strings (specific issues found)\n'
        '- recommendations: list of strings (suggested actions)\n'
        'Return ONLY valid JSON, no markdown or explanation.'
    ),
    'HIPAA': (
        'You are a HIPAA compliance expert. Analyze the following document text for HIPAA compliance issues.\n'
        'Check for: protected health information (PHI) handling, access controls, '
        'encryption requirements, business associate agreements, breach notification rules, '
        'minimum necessary standard, patient rights.\n'
        'Return your analysis as a JSON object with these exact keys:\n'
        '- risk_score: float 0.0 to 1.0\n'
        '- risk_level: "low" or "medium" or "high"\n'
        '- findings: list of strings (specific issues found)\n'
        '- recommendations: list of strings (suggested actions)\n'
        'Return ONLY valid JSON, no markdown or explanation.'
    )
}

def analyze_document(document_text, framework='GDPR', model_name='llama-3.1-8b-instant'):
    """Analyze document text against a compliance framework using LLM."""
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    # Truncate text if too long (LLM context limit)
    max_chars = 6000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + '\n[... document truncated for analysis ...]'
    
    system_prompt = FRAMEWORK_PROMPTS.get(framework, FRAMEWORK_PROMPTS['GDPR'])
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'Analyze this document:\n\n{document_text}'}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        raw = response.choices[0].message.content.strip()
        # Try to extract JSON from response
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        
        result = json.loads(raw)
        
        # Validate required keys
        return {
            'risk_score': float(result.get('risk_score', 0.5)),
            'risk_level': result.get('risk_level', 'medium'),
            'findings': result.get('findings', ['Analysis completed but no specific findings extracted.']),
            'recommendations': result.get('recommendations', ['Please review the document manually.'])
        }
    except json.JSONDecodeError:
        # If LLM doesn't return valid JSON, create a structured response from raw text
        return {
            'risk_score': 0.5,
            'risk_level': 'medium',
            'findings': [raw[:500] if raw else 'Analysis could not be parsed.'],
            'recommendations': ['Re-run the analysis or review the document manually.']
        }
    except Exception as e:
        return {
            'risk_score': 0.0,
            'risk_level': 'unknown',
            'findings': [f'Error during analysis: {str(e)}'],
            'recommendations': ['Check your API key and try again.']
        }
