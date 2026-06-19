import time
import sys

def type_text(text, speed=0.03, color="\033[92m"): # Default Green
    for char in text:
        sys.stdout.write(f"{color}{char}\033[0m")
        sys.stdout.flush()
        time.sleep(speed)
    print()

print("\n\n")
type_text("[SYSTEM] Intercepting CI/CD Pipeline Failure...", color="\033[94m") # Blue
time.sleep(1)
type_text("[SWARM] Initializing Autonomous DevOps Agents...", color="\033[94m")
time.sleep(1)
type_text(">>> Diagnostician Agent: Analyzing stack trace...", color="\033[93m") # Yellow
time.sleep(1.5)
type_text(">>> Diagnostician Agent: Root cause identified -> 'GROQ_API_KEY' missing in environment.", color="\033[93m")
time.sleep(1)
type_text(">>> Coder Agent: Drafting patch for .github/workflows/pytest.yml...", color="\033[96m") # Cyan
time.sleep(2)
type_text(">>> Coder Agent: Patch generated. Injecting conditional secrets check.", color="\033[96m")
time.sleep(1)
type_text(">>> Verifier Agent: Running local sandbox tests...", color="\033[95m") # Magenta
time.sleep(2)
type_text(">>> Verifier Agent: Tests passed. Pipeline resilience verified.", color="\033[95m")
time.sleep(1)
type_text("[SYSTEM] Committing patch and opening Pull Request: 'fix: gracefully handle missing secrets'", color="\033[92m") # Green
time.sleep(1)
type_text("[SUCCESS] Swarm execution complete. System returning to standby.\n\n", color="\033[92m")
