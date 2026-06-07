import requests

def parse_pr_url(url: str) -> dict:
    """Extract owner, repo, and PR number from a GitHub PR URL."""
    # Remove trailing slash if present
    url = url.rstrip("/")
    parts = url.split("/")
    # Expected format: https://github.com/owner/repo/pull/123
    return {
        "owner": parts[3],
        "repo": parts[4],
        "pr_number": parts[6]
    }

def fetch_pr_details(owner: str, repo: str, pr_number: str) -> dict:
    """Fetch PR metadata from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"GitHub API returned {response.status_code}: {response.text}"}
    
    data = response.json()
    return {
        "title": data.get("title"),
        "author": data.get("user", {}).get("login"),
        "base_branch": data.get("base", {}).get("ref"),
        "head_branch": data.get("head", {}).get("ref"),
        "changed_files": data.get("changed_files"),
        "additions": data.get("additions"),
        "deletions": data.get("deletions"),
        "state": data.get("state")
    }

def fetch_pr_diff(owner: str, repo: str, pr_number: str) -> str:
    """Fetch the raw unified diff of a PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return f"Error fetching diff: {response.status_code}"
    
    return response.text


if __name__ == "__main__":
    pr_url = "https://github.com/pallets/flask/pull/5446"
    
    print("=== PARSING PR URL ===")
    parsed = parse_pr_url(pr_url)
    print(parsed)
    
    owner = parsed["owner"]
    repo = parsed["repo"]
    pr_number = parsed["pr_number"]
    
    print("\n=== PR DETAILS ===")
    details = fetch_pr_details(owner, repo, pr_number)
    for key, value in details.items():
        print(f"{key:<15}: {value}")
    
    print("\n=== DIFF PREVIEW ===")
    diff = fetch_pr_diff(owner, repo, pr_number)
    print(diff[:500])