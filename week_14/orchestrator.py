from agents import diagnoser, developer, verifier, pr_agent

class SwarmOrchestrator:
    def __init__(self):
        self.max_loops = 3

    def handle_webhook_failure(self, initial_error_log: str):
        print("🚨 [WEBHOOK INTERCEPTED] CI/CD Pipeline Failure Detected!")
        print("🤖 Waking up the Self-Healing Swarm...\n")

        # Step 1: Diagnose
        diagnosis = diagnoser.run(f"Here is the CI/CD error log:\n{initial_error_log}")
        
        # Swarm Loop
        loop_count = 0
        current_context = diagnosis
        
        while loop_count < self.max_loops:
            loop_count += 1
            print(f"\n🔄 --- Swarm Loop {loop_count} ---")
            
            # Step 2: Develop
            dev_response = developer.run(f"Here is the diagnosis/context. Fix the code:\n{current_context}")
            
            # Step 3: Verify
            verification_result = verifier.run("The developer applied a fix. Run the tests and check if it passed.")
            
            if "failed" in verification_result.lower() or "error" in verification_result.lower():
                print(f"❌ Verification failed. Sending back to Developer...")
                current_context = f"The previous fix failed. Here are the new test results:\n{verification_result}"
                continue
            else:
                print(f"✅ Verification passed! The bug is squashed.")
                
                # Step 4: Create PR
                pr_summary = pr_agent.run(f"Diagnosis: {diagnosis}\nFix details: {dev_response}")
                
                print("\n🚀 [AUTO-DEPLOY] Opening Pull Request...")
                print("========================================")
                print(pr_summary)
                print("========================================")
                return True
                
        print("🛑 Swarm reached max loops. The bug is too complex. Pinging a human engineer.")
        return False
