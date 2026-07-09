from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import groq
from dotenv import load_dotenv
from typing import Any

load_dotenv()

app = FastAPI(title="Universal Customer Churn Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model Pipelines
BASE_DIR = os.path.dirname(__file__)
SAAS_MODEL_PATH = os.path.join(BASE_DIR, 'churn_model_pipeline.pkl')
TELECOM_MODEL_PATH = os.path.join(BASE_DIR, 'telecom_model_pipeline.pkl')

try:
    saas_model = joblib.load(SAAS_MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load SaaS model. Error: {e}")
    saas_model = None

try:
    telecom_model = joblib.load(TELECOM_MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load Telecom model. Error: {e}")
    telecom_model = None

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class CustomerList(BaseModel):
    customers: list[dict[str, Any]]

@app.post("/predict")
async def predict_churn(data: CustomerList):
    if not data.customers:
        return {"predictions": []}
    
    # Auto-detect schema based on the first row
    first_row = data.customers[0]
    
    if "mrr_usd" in first_row or "industry" in first_row:
        model_pipeline = saas_model
        dataset_type = "SaaS"
    elif "Age" in first_row or "Total Spend" in first_row:
        model_pipeline = telecom_model
        dataset_type = "Telecom"
    else:
        raise HTTPException(status_code=400, detail="Unknown dataset schema. Could not route to a model.")
        
    if not model_pipeline:
        raise HTTPException(status_code=500, detail=f"{dataset_type} model pipeline not loaded.")
    
    # Convert incoming data to DataFrame
    df = pd.DataFrame(data.customers)
    
    # Predict probabilities (return probability of class 1 - churn)
    probs = model_pipeline.predict_proba(df)[:, 1]
    
    results = []
    for i, p in enumerate(probs):
        results.append({
            "index": i,
            "churn_probability": round(float(p), 4),
            "is_high_risk": bool(p > 0.65),
            "dataset_type": dataset_type
        })
        
    return {"predictions": results}

@app.post("/explain")
async def explain_churn(customer: dict[str, Any]):
    """
    Uses LLaMA 3 via Groq to explain why the customer is high risk and how to save them.
    Dynamically builds prompt based on whatever data is passed.
    """
    if not groq_client:
        return {"result": "Groq API Key not found. Cannot generate AI explanation."}
    
    # Determine domain context
    if "mrr_usd" in customer:
        domain = "SaaS B2B Enterprise"
    else:
        domain = "B2C Telecom"
        
    # Build dynamic profile string
    profile_str = "\n".join([f"- {k}: {v}" for k, v in customer.items()])
    
    prompt = f"""
    You are an expert {domain} Customer Retention Specialist. 
    Analyze this high-risk customer and provide a 3-sentence strategy to save them.
    
    Customer Profile:
    {profile_str}
    
    Provide the response in two clear sections:
    1. EXPLANATION: (1 sentence explaining why they are at risk based on the specific metrics above)
    2. ACTION PLAN: (2 sentences on exactly what to do to save them right now)
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
