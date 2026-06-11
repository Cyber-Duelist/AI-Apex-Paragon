import os
import json
from dotenv import load_dotenv
from groq import Groq

# Import our custom observability tool
from tracer import Tracer

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
eval_tracer = Tracer()

# 1. The Golden Dataset
GOLDEN_DATASET = [
    {
        "question": "What is the risk level of the Merger Agreement?",
        "answer": "The Merger Agreement is high risk with a score of 0.9.",
        "rubric": "5 = mentions high risk and score. 1 = no risk info."
    },
    {
        "question": "Who approved the transaction?",
        "answer": "The board of directors approved it.",
        "rubric": "5 = mentions board of directors. 1 = wrong or missing."
    },
    {
        "question": "What premium will shareholders receive?",
        "answer": "Shareholders will receive a 15 percent premium.",
        "rubric": "5 = mentions 15 percent. 1 = wrong number or missing."
    },
    {
        "question": "What happens to Company B?",
        "answer": "Company B will become a wholly owned subsidiary.",
        "rubric": "5 = mentions subsidiary. 1 = wrong or vague."
    },
    {
        "question": "When was the agreement signed?",
        "answer": "I am not sure when it was signed.",
        "rubric": "5 = mentions January 10 2024. 1 = wrong or missing date."
    }
]

# 2. The Traced Judge Call
@eval_tracer.trace()
def call_judge_api(question: str, answer: str, rubric: str):
    """Makes the raw API call to Groq, allowing our Tracer to intercept and measure it."""
    system_prompt = """
    You are an impartial, highly rigorous AI evaluation judge. 
    Score the AI Answer on a scale of 1 to 5 based strictly on the Rubric.
    CRITICAL: Output ONLY valid JSON with two keys: "score" (int) and "reasoning" (string).
    """
    user_prompt = f"[User Question]\n{question}\n\n[AI Answer]\n{answer}\n\n[Grading Rubric]\n{rubric}"
    
    MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    
    for current_model in MODELS:
        try:
            return client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            print(f"Model {current_model} failed: {str(e)}. Falling back.")
            continue
            
    raise Exception("All judge models failed.")

def evaluate_and_trace(question: str, answer: str, rubric: str) -> dict:
    """Helper function to parse the JSON returned by the traced API call."""
    raw_text = call_judge_api(question, answer, rubric)
    try:
        return json.loads(raw_text)
    except:
        return {"score": 1, "reasoning": "Failed to parse JSON"}

# 3. The Dashboard Loop
if __name__ == "__main__":
    print("=== RUNNING EVALUATION DASHBOARD ===\n")
    
    total_questions = len(GOLDEN_DATASET)
    pass_count = 0
    total_score = 0
    
    for i, item in enumerate(GOLDEN_DATASET, 1):
        # Run the evaluation
        eval_result = evaluate_and_trace(item["question"], item["answer"], item["rubric"])
        
        # Extract the score
        score = eval_result.get("score", 1)
        total_score += score
        
        # Calculate Verdict
        verdict = "PASS" if score >= 4 else "FAIL"
        if verdict == "PASS":
            pass_count += 1
            
        # Extract Telemetry from the Tracer's memory
        latest_trace = eval_tracer.traces[-1]
        latency = latest_trace["duration_ms"]
        cost = latest_trace["estimated_cost_usd"]
        
        # Format strings for a clean terminal output
        q_trunc = (item['question'][:25] + '...') if len(item['question']) > 25 else item['question']
        
        print(f"Q{i}: {q_trunc:<28} Score: {score}/5  {verdict:<5} {latency}ms  ${cost:.6f}")

    # Calculate final metrics
    pass_rate = (pass_count / total_questions) * 100
    avg_score = total_score / total_questions
    
    summary = eval_tracer.get_summary()
    total_cost = float(summary["Total cost"].replace('$', ''))
    avg_latency = summary["Avg latency"]

    print("\n=== SUMMARY ===")
    print(f"Total      : {total_questions}")
    print(f"Pass Rate  : {pass_rate:.1f}%")
    print(f"Avg Score  : {avg_score:.1f}/5")
    print(f"Avg Latency: {avg_latency}")
    print(f"Total Cost : ${total_cost:.6f}")