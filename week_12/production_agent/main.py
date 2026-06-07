from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import datetime
import time

# Import the core agent logic and our bulletproof logger
from agent import ProductionAgent
from logs import system_logger

# ==========================================
# 1. INITIALIZE API & AGENT
# ==========================================
app = FastAPI(
    title="Enterprise Compliance Auditor API",
    description="Autonomous AI microservice for legal risk assessment and policy enforcement.",
    version="1.0.0"
)

print("Booting Compliance Auditor Service...")
auditor_agent = ProductionAgent()

# ==========================================
# 2. DEFINE DATA MODELS
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
    return {"service": "Compliance Auditor", "status": "online"}

@app.post("/audit", response_model=AuditResponse)
def audit_endpoint(request: AuditRequest):
    """The main communication port for the Audit Agent."""
    start_time = time.time()
    
    try:
        # 1. Execute the ReAct loop
        agent_answer = auditor_agent.process_request(request.query)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 2. Check Security Guardrails & Log
        if "[SECURITY BLOCK]" in agent_answer:
            system_logger.log_trace(request.user_id, request.query, "blocked_by_policy", agent_answer, duration_ms)
            return {
                "status": "blocked_by_policy",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "response": agent_answer
            }
            
        # 3. Log Success & Return
        system_logger.log_trace(request.user_id, request.query, "success", agent_answer, duration_ms)
        return {
            "status": "success",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "response": agent_answer
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)
        system_logger.log_trace(request.user_id, request.query, "server_error", error_msg, duration_ms)
        raise HTTPException(status_code=500, detail=f"Agent Processing Error: {error_msg}")

# ==========================================
# 4. SERVER RUNNER
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting Enterprise Compliance API on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)