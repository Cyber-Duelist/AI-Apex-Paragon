import os
import json
from dotenv import load_dotenv
from groq import Groq
from github_client import fetch_pr_details, fetch_pr_diff, parse_pr_url

load_dotenv()

def get_available_model():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
    for model in preferred_models:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            print(f"Using model: {model}")
            return model
        except Exception:
            continue
    raise Exception("No available models found.")

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_model = get_available_model()

def review_pr(owner: str, repo: str, pr_number: str) -> dict:
    client = _client
    model = _model

    # Fetch PR data
    details = fetch_pr_details(owner, repo, pr_number)
    if "error" in details:
        return {"error": details["error"]}

    diff = fetch_pr_diff(owner, repo, pr_number)
    if not diff or diff.startswith("Error"):
        return {"error": "Could not fetch diff"}

    # Truncate to avoid token limits
    diff_truncated = diff[:3000]

    system_prompt = """You are an expert code reviewer. 
Review the PR diff and return ONLY valid JSON with these exact keys:
- summary: one sentence describing what this PR does
- bugs: list of potential bugs found (empty list if none)
- security_issues: list of security concerns (empty list if none)
- suggestions: list of improvement suggestions
- severity: overall severity as "low", "medium", or "high"
- approved: true if code looks good, false if changes needed"""

    user_prompt = f"""PR Title: {details['title']}
Author: {details['author']}
Changed Files: {details['changed_files']}

Diff:
{diff_truncated}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    pr_url = "https://github.com/pallets/flask/pull/5446"
    parsed = parse_pr_url(pr_url)

    print("=== CODE REVIEW ===")
    review = review_pr(parsed["owner"], parsed["repo"], parsed["pr_number"])

    if "error" in review:
        print(f"Error: {review['error']}")
    else:
        print(f"Summary    : {review.get('summary')}")
        print(f"Bugs       : {review.get('bugs')}")
        print(f"Security   : {review.get('security_issues')}")
        print(f"Suggestions: {review.get('suggestions')}")
        print(f"Severity   : {review.get('severity')}")
        print(f"Approved   : {review.get('approved')}")