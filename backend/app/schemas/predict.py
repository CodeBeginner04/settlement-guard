from pydantic import BaseModel
from typing import Dict, Any

class TradeRequest(BaseModel):
    Notional_Amount_USD: float
    Market_Volatility_Index: float
    Asset_Class: str
    Counterparty_Rating: str
    SSI_Status: str
    Liquidity_Score: str
    # Add other features required by the pipeline if necessary, 
    # but these are the main ones mentioned in the prompt.
    # The pipeline trained on: 
    # ['Trade_Day', 'Trade_Hour', 'Asset_Class', 'Counterparty_Rating', 
    # 'Custodian_Location', 'SSI_Status', 'Liquidity_Score', 
    # 'Market_Volatility_Index', 'Operation_Type', 'Currency', 'Notional_Amount_USD']
    # We should probably ask for all of them to be safe, defaulting others if needed.
    # For this specific user request, they listed specific fields, let's stick to those + defaults for others.
    
    # Defaults/Extras to satisfy pipeline structure
    Custodian_Location: str = "US"
    Operation_Type: str = "DVP"
    Currency: str = "USD"
    Trade_Day: str = "Monday"
    Trade_Hour: float = 12.0

    class Config:
        json_schema_extra = {
            "example": {
                "Notional_Amount_USD": 5000000.0,
                "Market_Volatility_Index": 18.5,
                "Asset_Class": "Corp Bond",
                "Counterparty_Rating": "CCC",
                "SSI_Status": "Mismatch",
                "Liquidity_Score": "Low",
                "Custodian_Location": "US",
                "Operation_Type": "DVP",
                "Currency": "USD",
                "Trade_Day": "Friday",
                "Trade_Hour": 16.5
            }
        }

class PredictionResponse(BaseModel):
    failure_probability: float
    risk_level: str
    shap_explanation: Dict[str, Any]
