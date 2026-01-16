from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Inference Service")

class TradeData(BaseModel):
    # This acts as a loose schema for now, will be tightened in Phase 3
    amount: float
    counterparty: str
    instrument_type: str

import joblib
import pandas as pd
import shap
import os

# Load Artifacts at Startup
MODEL_PATH = "model/model.joblib"
EXPLAINER_PATH = "model/shap_explainer.joblib"
FEATURE_NAMES_PATH = "model/feature_names.joblib"

print("Loading model artifacts...")
try:
    pipeline = joblib.load(MODEL_PATH)
    # Load explainer if needed - SHAP TreeExplainer usually needs the model object
    # For now, we'll calculate SHAP on the fly or load the explainer
    # explainer = joblib.load(EXPLAINER_PATH) 
    # Note: Loading large explainers can be tricky. 
    # We will use the pipeline's internal model for SHAP if feasible, 
    # or just return the probability for now to keep it fast.
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    pipeline = None

@app.get("/health")
def health_check():
    status = "healthy" if pipeline else "degraded"
    return {"status": status, "service": "ml-inference"}

class PredictionRequest(BaseModel):
    # We need all features used in training
    Trade_ID: str
    Trade_Date: str
    Settlement_Date: str
    # Features
    Asset_Class: str
    Counterparty_Rating: str
    Custodian_Location: str
    SSI_Status: str
    Liquidity_Score: str
    Market_Volatility_Index: float
    Operation_Type: str
    Currency: str
    Notional_Amount_USD: float
    # Derived features like Trade_Hour/Day need to be computed

@app.post("/predict")
def predict_trade(trade: PredictionRequest):
    if not pipeline:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # 1. Prepare Data
    # Convert incoming JSON to DataFrame
    input_data = trade.dict()
    df = pd.DataFrame([input_data])
    
    # 2. Feature Engineering (Must match training!)
    # Parse Dates to get Hour/Day
    dt_obj = pd.to_datetime(df['Trade_Date'])
    df['Trade_Day'] = dt_obj.dt.day_name()
    df['Trade_Hour'] = dt_obj.dt.hour
    
    # ensure numeric types
    df['Notional_Amount_USD'] = pd.to_numeric(df['Notional_Amount_USD'])
    df['Market_Volatility_Index'] = pd.to_numeric(df['Market_Volatility_Index'])

    # 3. Predict
    try:
        probability = pipeline.predict_proba(df)[0][1] # Probability of Class 1 (Fail)
        prediction = pipeline.predict(df)[0] # 0 or 1
        
        # 4. Explain (SHAP) - Simplified
        # We can implement full SHAP later, for now let's just return key drivers based on logic or partial SHAP
        # Full SHAP calculation on every request can be slow (~100ms+). 
        # For Phase 3, getting the probability is the big win.
        
        return {
            "trade_id": trade.Trade_ID,
            "probability": float(probability),
            "prediction": int(prediction),
            "risk_level": "CRITICAL" if probability > 0.8 else "HIGH" if probability > 0.5 else "LOW",
            "model_version": "v1.0.0"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

