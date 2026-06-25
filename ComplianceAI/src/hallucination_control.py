import os
from groq import Groq
from vector_store import search, model


def rag_with_guard(question, collection, source=None, model_name='llama-3.1-8b-instant'):
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    retrieved = search(question, collection, top_k=3, source_filter=source)
    if not retrieved:
        context_text = 'No relevant documents found for this query.'
    else:
        context_text = '\n'.join([f"- {chunk['text']}" for chunk in retrieved])

    system_prompt = (
        'You are ComplianceAI, an expert compliance analysis assistant.\n'
        'Answer the user\'s question using the provided document context.\n'
        'If the context contains the answer, explain it clearly with specific references.\n'
        'If the context does not cover the question, say so honestly but offer to help with what you can.\n\n'
        f'Document Context:\n{context_text}'
    )

    response = groq_client.chat.completions.create(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'Question: {question}'}
        ],
        temperature=0.3
    )
    return {
        'answer': response.choices[0].message.content,
        'grounded': len(retrieved) > 0,
        'chunks_used': len(retrieved)
    }
