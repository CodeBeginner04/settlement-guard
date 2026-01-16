from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
import os
from .schemas.predict import TradeRequest, PredictionResponse
from .db.session import engine
from .db.models import Base

# Create Tables (Existing logic)
Base.metadata.create_all(bind=engine)

# --- 1. Global State for Model (Singleton Pattern) ---
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the heavy model ONLY when the server starts
    print("Loading ML Pipeline...")
    # Use Environment Variable provided by Docker Compose, default to local relative path
    model_path = os.getenv("MODEL_PATH", "../ml_service/model/model.joblib")
    explainer_path = os.getenv("EXPLAINER_PATH", "../ml_service/model/shap_explainer.joblib")
    
    try:
        if os.path.exists(model_path):
            ml_models["pipeline"] = joblib.load(model_path)
            # ml_models["explainer"] = joblib.load(explainer_path) 
            print(f"Model loaded from {model_path}. API Ready.")
        else:
             print(f"Error: Model not found at {model_path}")

    except Exception as e:
        print(f"Failed to load model: {e}")
        
    yield
    # Clean up resources if needed
    ml_models.clear()

app = FastAPI(lifespan=lifespan, title="SettlementGuard API")

# --- CORS ---
origins = [
    "http://localhost:5173", # Vite Default
    "http://localhost:3000", 
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    status = "healthy" if "pipeline" in ml_models else "no_model"
    return {"status": status, "service": "api-gateway"}

# --- 3. The Endpoint ---
@app.post("/predict", response_model=PredictionResponse)
async def predict_settlement_failure(trade: TradeRequest):
    pipeline = ml_models.get("pipeline")
    if not pipeline:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Convert incoming JSON -> Pandas DataFrame
    input_data = pd.DataFrame([trade.dict()])

    # A. Get Probability
    # [:, 1] gets the probability of Class 1 (Failure)
    try:
        prob = pipeline.predict_proba(input_data)[0, 1] 
    except Exception as e:
        print(f"Prediction Error: {e}")
        # Fallback for demo if feature mismatch
        raise HTTPException(status_code=400, detail=f"Prediction Error: {str(e)}")

    # B. Define Risk Level
    risk_level = "CRITICAL" if prob > 0.8 else "HIGH" if prob > 0.5 else "LOW"

    # C. Explainability (SHAP)
    # We need to transform the data first because SHAP works on the transformed features
    explanation = {
        "base_value": 0.0,
        "feature_contributions": []
    }
    
    # Simplified SHAP for stability directly in API (full SHAP can be heavy/brittle)
    # If we loaded the explainer successfully:
    if "explainer" in ml_models:
        try:
            preprocessor = pipeline.named_steps['preprocessor']
            transformed_data = preprocessor.transform(input_data)
            explainer = ml_models["explainer"]
            shap_values = explainer.shap_values(transformed_data)
            
            # Format SHAP
            explanation = {
                "base_value": float(explainer.expected_value),
                "feature_contributions": [float(val) for val in shap_values[0]]
            }
        except Exception as e:
            print(f"SHAP Error: {e}")

    return {
        "failure_probability": round(float(prob), 4),
        "risk_level": risk_level,
        "shap_explanation": explanation
    }
