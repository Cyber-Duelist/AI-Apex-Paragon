import os
import json
from dotenv import load_dotenv
from groq import Groq

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_response(question: str, answer: str, rubric: str) -> dict:
    """
    Uses an LLM as an automated judge to score a response based on a specific rubric.
    """
    system_prompt = """
    You are an impartial, highly rigorous AI evaluation judge. 
    You will be provided with a User Question, an AI Answer, and a Grading Rubric.
    
    You must score the AI Answer on a scale of 1 to 5 based strictly on the Rubric.
    
    CRITICAL: You must output ONLY valid JSON with exactly two keys:
    1. "score": An integer between 1 and 5.
    2. "reasoning": A brief, 1-2 sentence explanation of why you gave this score based on the rubric.
    """

    user_prompt = f"""
    [User Question]
    {question}
    
    [AI Answer]
    {answer}
    
    [Grading Rubric]
    {rubric}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # The judge needs high reasoning capabilities
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0, # 0.0 forces maximum determinism for reliable grading
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0, "reasoning": f"Evaluation failed: {str(e)}"}

if __name__ == "__main__":
    print("=== INITIALIZING LLM-AS-A-JUDGE ===\n")
    
    question = "Can you summarize the Acquisition Contract?"
    rubric = "1 = Total hallucination or refusal. 3 = Basic summary but missing details. 5 = Comprehensive, accurate, and mentions the exact risk level."

    # Test 1: A terrible answer
    bad_answer = "The contract is about buying a company. I think it is safe."
    print("Evaluating Bad Answer...")
    bad_result = evaluate_response(question, bad_answer, rubric)
    print(f"Score: {bad_result['score']}/5")
    print(f"Reasoning: {bad_result['reasoning']}\n")

    # Test 2: An excellent answer
    good_answer = "The Acquisition Contract outlines the purchase of Company B. It is classified as High Risk (score 0.9) due to the lack of a non-compete clause, requiring senior management approval."
    print("Evaluating Good Answer...")
    good_result = evaluate_response(question, good_answer, rubric)
    print(f"Score: {good_result['score']}/5")
    print(f"Reasoning: {good_result['reasoning']}\n")