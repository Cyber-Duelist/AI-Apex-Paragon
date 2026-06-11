import os
import subprocess
from orchestrator import SwarmOrchestrator

def simulate_webhook():
    print("Simulating a CI/CD test run...\n")
    
    # 1. Run the tests to get the initial failure log
    repo_path = os.path.join(os.path.dirname(__file__), "mock_repo")
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_calculator.py", "-v"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    # 2. If it fails, fire the webhook to the Swarm
    if result.returncode != 0:
        error_log = result.stdout + "\n" + result.stderr
        
        orchestrator = SwarmOrchestrator()
        orchestrator.handle_webhook_failure(error_log)
    else:
        print("Tests are already passing! Nothing to heal.")

if __name__ == "__main__":
    simulate_webhook()
