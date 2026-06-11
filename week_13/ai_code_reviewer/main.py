import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from github_client import parse_pr_url, fetch_pr_details
from reviewer import review_pr, _model

app = FastAPI(title="AI Code Reviewer")

# Pydantic Models
class ReviewRequest(BaseModel):
    pr_url: str

class ReviewResponse(BaseModel):
    pr_url: str
    title: str
    author: str
    summary: str
    bugs: list
    security_issues: list
    suggestions: list
    severity: str
    approved: bool


# Endpoints
@app.get("/")
def root():
    return {"status": "AI Code Reviewer is running"}

@app.get("/health")
def health():
    return {"status": "ok", "model": _model}

@app.post("/review", response_model=ReviewResponse)
def review(req: ReviewRequest):
    # Parse URL
    try:
        parsed = parse_pr_url(req.pr_url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid GitHub PR URL format")

    owner = parsed["owner"]
    repo = parsed["repo"]
    pr_number = parsed["pr_number"]

    # Fetch PR details
    details = fetch_pr_details(owner, repo, pr_number)
    if "error" in details:
        raise HTTPException(status_code=404, detail=details["error"])

    # Run LLM review
    review_result = review_pr(owner, repo, pr_number)
    if "error" in review_result:
        raise HTTPException(status_code=500, detail=review_result["error"])

    return ReviewResponse(
        pr_url=req.pr_url,
        title=details.get("title", ""),
        author=details.get("author", ""),
        summary=review_result.get("summary", ""),
        bugs=review_result.get("bugs", []),
        security_issues=review_result.get("security_issues", []),
        suggestions=review_result.get("suggestions", []),
        severity=review_result.get("severity", "low"),
        approved=review_result.get("approved", False)
    )