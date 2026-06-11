# Case Study: AI Pull Request Reviewer

## 🔴 The Problem
Senior engineers spend an average of 20-30% of their week reviewing Pull Requests. This creates a massive bottleneck in the software development lifecycle. While static analysis tools (like SonarQube) catch basic syntax errors, they completely fail to catch architectural flaws, security vulnerabilities, or subtle logic errors in complex diffs.

## 🟢 The Solution
We built an automated **AI Code Review Service** (Week 13) that connects directly to the GitHub API. 

Developers simply submit a GitHub Pull Request URL. The service fetches the raw Git diff, parses the changed files, and streams the delta to a high-reasoning LLM (LLaMA 3.3 70B). The AI returns a highly structured, machine-readable JSON review that categorizes findings into `bugs`, `security_issues`, and `suggestions`, along with an overall severity rating.

## 🛠️ Architecture & Technologies
- **Backend:** `FastAPI`
- **Integrations:** `GitHub API` (diff extraction)
- **AI/LLM:** `Groq API`, `LLaMA 3.3 70B-Versatile`
- **Data Engineering:** Forced JSON-schema output generation for programmatic frontend rendering.

## 📈 Business Value
1. **Engineering Velocity:** Drastically reduces the time Pull Requests sit in the review queue.
2. **Shift-Left Security:** Catches vulnerabilities and logic errors before they are merged into the main branch.
3. **Actionable Insights:** By forcing the LLM to output structured JSON, the review can automatically block CI/CD pipelines if the `severity` key returns "high".
