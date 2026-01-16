from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    counterparty = Column(String, nullable=False)
    isin = Column(String, nullable=False)
    
    # Status: RECEIVED, PENDING_ANALYSIS, FAILED, SETTLED
    status = Column(String, default="RECEIVED")
    
    risk_score = Column(Float, nullable=True)
    prediction_details = Column(JSON, nullable=True) # Store SHAP values here
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
