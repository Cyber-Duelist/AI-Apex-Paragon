import os
import sys

# Ensure Python can find our local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from vector_store import get_collection
from hallucination_control import rag_with_guard

# 1. The Golden Dataset
# This is our undeniable source of truth. We know exactly what the AI SHOULD say.
GOLDEN_DATASET = [
    {"question": "When was the merger agreement signed?", "expected": "January 10, 2024"},
    {"question": "What premium will shareholders receive?", "expected": "15 percent"},
    {"question": "Where will disputes be settled?", "expected": "Delaware"},
    {"question": "What happens to Company B after completion?", "expected": "wholly-owned subsidiary"},
    {"question": "Who approved the transaction?", "expected": "board of directors"}
]

def evaluate(dataset, collection) -> dict:
    """
    Runs the dataset through the RAG pipeline and automatically grades the answers.
    """
    print("=== RUNNING EVALUATION ===")
    total = len(dataset)
    grounded_count = 0
    correct_count = 0
    failed_count = 0

    for i, item in enumerate(dataset, 1):
        question = item["question"]
        expected = item["expected"]

        # Run the query through our secure pipeline
        res = rag_with_guard(question, collection)
        
        # Format answer cleanly for the terminal (remove newlines)
        answer = res["answer"].replace('\n', ' ')
        is_grounded = res["grounded"]

        if is_grounded:
            grounded_count += 1

        # The Grader: Does the LLM answer contain the exact expected keyword?
        # We use .lower() so "Delaware" and "delaware" both pass.
        if expected.lower() in answer.lower():
            correct_count += 1
            result_status = "PASS"
        else:
            failed_count += 1
            result_status = "FAIL"

        # Print the live testing trace
        print(f"Q{i}: {question}")
        print(f"   Expected : {expected}")
        print(f"   Answer   : {answer}")
        print(f"   Result   : {result_status}")
        print("-" * 50)

    # Calculate final math
    accuracy = (correct_count / total) * 100 if total > 0 else 0.0

    return {
        "Total questions": total,
        "Grounded": grounded_count,
        "Correct": correct_count,
        "Failed": failed_count,
        "Accuracy": f"{accuracy:.1f}%"
    }

if __name__ == "__main__":
    # Initialize connection to our ChromaDB
    collection = get_collection()
    
    # Run the Eval
    summary = evaluate(GOLDEN_DATASET, collection)

    # Print the Final Report
    print("=== EVALUATION SUMMARY ===")
    for key, value in summary.items():
        # The :<15 formats the text to align neatly in the terminal
        print(f"{key:<15} : {value}")