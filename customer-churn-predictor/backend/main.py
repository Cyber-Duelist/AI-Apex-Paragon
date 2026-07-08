from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Customer Churn Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model Pipeline
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'churn_model_pipeline.pkl')
try:
    model_pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model. Ensure train_model.py has been run. Error: {e}")
    model_pipeline = None

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class CustomerData(BaseModel):
    industry: str
    company_size: int
    mrr_usd: float
    contract_type: str
    tenure_months: int
    active_users: int
    api_calls_per_month: int
    support_tickets_last_30d: int
    feature_adoption_rate: float
    last_login_days_ago: int

class CustomerList(BaseModel):
    customers: list[CustomerData]

@app.post("/predict")
async def predict_churn(data: CustomerList):
    if not model_pipeline:
        raise HTTPException(status_code=500, detail="Model pipeline not loaded.")
    
    # Convert incoming data to DataFrame
    df = pd.DataFrame([c.dict() for c in data.customers])
    
    # Predict probabilities (return probability of class 1 - churn)
    probs = model_pipeline.predict_proba(df)[:, 1]
    
    results = []
    for i, p in enumerate(probs):
        results.append({
            "index": i,
            "churn_probability": round(float(p), 4),
            "is_high_risk": bool(p > 0.65)
        })
        
    return {"predictions": results}

@app.post("/explain")
async def explain_churn(customer: CustomerData):
    """
    Uses LLaMA 3 via Groq to explain why the customer is high risk and how to save them.
    """
    if not groq_client:
        return {"explanation": "Groq API Key not found. Cannot generate AI explanation.", "action_plan": []}
    
    prompt = f"""
    You are an expert SaaS Customer Success Manager. 
    Analyze this high-risk customer and provide a 3-sentence strategy to save them.
    
    Customer Profile:
    - Industry: {customer.industry}
    - Company Size: {customer.company_size} employees
    - Monthly Revenue (MRR): ${customer.mrr_usd}
    - Contract Type: {customer.contract_type}
    - Tenure: {customer.tenure_months} months
    - Feature Adoption Rate: {customer.feature_adoption_rate * 100}%
    - Support Tickets (Last 30 Days): {customer.support_tickets_last_30d}
    - Last Login: {customer.last_login_days_ago} days ago
    
    Provide the response in two clear sections:
    1. EXPLANATION: (1 sentence explaining why they are at risk)
    2. ACTION PLAN: (2 sentences on exactly what to do to save them)
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256
        )
        content = response.choices[0].message.content
        return {"result": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
