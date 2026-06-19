import time
import sys

def type_text(text, speed=0.03, color="\033[92m"): # Default Green
    for char in text:
        sys.stdout.write(f"{color}{char}\033[0m")
        sys.stdout.flush()
        time.sleep(speed)
    print()

print("\n\n")
type_text("[INFO] Listening for GitHub PR Webhooks...", color="\033[94m") # Blue
time.sleep(1)
type_text("[EVENT] Received Pull Request #42 on repo 'backend-api'", color="\033[93m") # Yellow
time.sleep(1)
type_text("[FETCH] Retrieving diff for PR #42 via GitHub API...", color="\033[94m")
time.sleep(1.5)
type_text("[AI] Analyzing 435 lines of code across 3 files...", color="\033[95m") # Magenta
time.sleep(2)
type_text(">>> Found 1 High Severity Security Vulnerability (SQL Injection Risk in auth.py).", color="\033[91m") # Red
time.sleep(1)
type_text(">>> Found 2 Minor Code Smells (Unused imports in utils.py).", color="\033[93m") # Yellow
time.sleep(1)
type_text("[SYSTEM] Compiling structured review report...", color="\033[94m")
time.sleep(1)
type_text("[GITHUB] Posting review to PR #42 -> Status: REQUEST_CHANGES", color="\033[96m") # Cyan
time.sleep(1)
type_text("[SUCCESS] Code Review Complete. Awaiting developer updates.\n\n", color="\033[92m")
