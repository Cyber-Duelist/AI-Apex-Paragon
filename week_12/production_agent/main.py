from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import datetime

# Import the core agent logic you built
from agent import ProductionAgent

# ==========================================
# 1. INITIALIZE API & AGENT
# ==========================================
app = FastAPI(
    title="Enterprise Compliance Auditor API",
    description="Autonomous AI microservice for legal risk assessment and policy enforcement.",
    version="1.0.0"
)

print("Booting Compliance Auditor Service...")
# The agent spins up once when the server starts
auditor_agent = ProductionAgent()

# ==========================================
# 2. DEFINE DATA MODELS (Pydantic)
# ==========================================
class AuditRequest(BaseModel):
    query: str
    user_id: str = "system_default"

class AuditResponse(BaseModel):
    status: str
    timestamp: str
    response: str

# ==========================================
# 3. API ENDPOINTS
# ==========================================
@app.get("/health")
def health_check():
    """DevOps endpoint to verify the service is running."""
    return {
        "service": "Compliance Auditor",
        "status": "online",
        "active_model": auditor_agent.model
    }

@app.post("/audit", response_model=AuditResponse)
def audit_endpoint(request: AuditRequest):
    """The main communication port for the Audit Agent."""
    try:
        # Execute the ReAct loop
        agent_answer = auditor_agent.process_request(request.query)
        
        # Check if the security guardrail intercepted a malicious prompt
        if "[SECURITY BLOCK]" in agent_answer:
            return {
                "status": "blocked_by_policy",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "response": agent_answer
            }
            
        return {
            "status": "success",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "response": agent_answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Processing Error: {str(e)}")

# ==========================================
# 4. SERVER RUNNER
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting Enterprise Compliance API on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)