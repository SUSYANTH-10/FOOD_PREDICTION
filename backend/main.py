# backend/main.py
import os
import joblib
import pandas as pd
import numpy as np
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
import database

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Intelligent Food Demand Prediction API",
    description="Backend API providing ML-driven food demand forecasting, safety preparation buffers, and database logging.",
    version="1.0.0",
)

# Enable CORS for Next.js Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# 2. Automatically Create Database Tables on Application Startup
models.Base.metadata.create_all(bind=database.engine)

# 3. Load Machine Learning Model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "rf_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model successfully loaded from {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"Warning: Model file could not be loaded from {MODEL_PATH}. Error: {e}")

# 4. Pydantic Schemas (API Request/Response Validation)
class PredictionRequest(BaseModel):
    item_name: str = Field(..., json_schema_extra={"example": "Chicken Rice"})
    past_sales: int = Field(..., ge=0, json_schema_extra={"example": 150})
    headcount: int = Field(..., ge=0, json_schema_extra={"example": 350})
    prep_qty: int = Field(..., ge=0, json_schema_extra={"example": 180})
    is_weekend: bool = Field(False, json_schema_extra={"example": False})
    is_rainy: bool = Field(False, json_schema_extra={"example": True})


class PredictionResponse(BaseModel):
    item_name: str
    predicted_demand: int
    recommended_prep: int
    unit: str = "plates"


class DailyLogCreate(BaseModel):
    item_name: str
    date: date
    past_sales: int = Field(..., ge=0)
    headcount: int = Field(..., ge=0)
    prep_qty: int = Field(..., ge=0)
    actual_sales: Optional[int] = Field(None, ge=0)
    leftover_qty: Optional[int] = Field(None, ge=0)
    is_weekend: bool = False
    is_rainy: bool = False


class DailyLogResponse(BaseModel):
    id: int
    date: str
    item_name: str
    past_sales: int
    headcount: int
    prep_qty: int
    actual_sales: Optional[int]
    leftover_qty: Optional[int]
    is_weekend: bool
    is_rainy: bool

    class Config:
        from_attributes = True


# 5. Core API Endpoints

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "online",
        "system": "Intelligent Food Demand Prediction API",
        "version": "1.0.0"
    }


@app.post("/api/v1/predict", response_model=PredictionResponse)
def predict_food_demand(payload: PredictionRequest):
    """
    ML Prediction Endpoint: Accepts demand factors, validates ranges,
    runs Random Forest inference, and applies a safety preparation buffer.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="ML model is not loaded on server.")

    # Business Logic Guardrail: Validate prep_qty bounds against input features
    if payload.prep_qty < payload.past_sales:
        raise HTTPException(
            status_code=400,
            detail="Invalid input bounds: prep_qty cannot be less than past_sales."
        )

    # Format input DataFrame matching training feature columns
    input_data = pd.DataFrame([{
        "past_sales": payload.past_sales,
        "headcount": payload.headcount,
        "prep_qty": payload.prep_qty,
        "is_weekend": int(payload.is_weekend),
        "is_rainy": int(payload.is_rainy)
    }])

    # Run Model Inference
    raw_prediction = model.predict(input_data)[0]
    predicted_demand = int(np.round(raw_prediction))

    # Apply 5% Safety Preparation Buffer
    recommended_prep = int(np.ceil(predicted_demand * 1.05))

    return PredictionResponse(
        item_name=payload.item_name,
        predicted_demand=predicted_demand,
        recommended_prep=recommended_prep,
        unit="plates"
    )


# 6. Database API Routes (Analytics History & Staff Data Entry)

@app.get("/api/v1/analytics/history", response_model=List[DailyLogResponse])
def get_historical_logs(limit: int = 50, db: Session = Depends(database.get_db)):
    """Fetch recent historical logs from SQLite database for analytics charts."""
    logs = (
        db.query(models.DailyLog)
        .order_by(models.DailyLog.date.desc())
        .limit(limit)
        .all()
    )

    result = []
    for log in logs:
        result.append(
            DailyLogResponse(
                id=log.id,
                date=str(log.date),
                item_name=log.item.name if log.item else "Unknown",
                past_sales=log.past_sales,
                headcount=log.headcount,
                prep_qty=log.prep_qty,
                actual_sales=log.actual_sales,
                leftover_qty=log.leftover_qty,
                is_weekend=log.is_weekend,
                is_rainy=log.is_rainy,
            )
        )
    return result


@app.post("/api/v1/logs", response_model=DailyLogResponse)
def create_daily_log(payload: DailyLogCreate, db: Session = Depends(database.get_db)):
    """
    Staff Data Entry Endpoint: Allows canteen staff to submit daily kitchen records
    directly into the database.
    """
    # Check if item exists in food_items table, or create a default catalog entry
    food_item = db.query(models.FoodItem).filter(models.FoodItem.name == payload.item_name).first()
    if not food_item:
        food_item = models.FoodItem(name=payload.item_name, category="General", cost_per_unit_inr=50.0)
        db.add(food_item)
        db.commit()
        db.refresh(food_item)

    # Compute leftover_qty automatically if actual_sales is provided but leftovers is None
    leftover = payload.leftover_qty
    if payload.actual_sales is not None and leftover is None:
        leftover = max(0, payload.prep_qty - payload.actual_sales)

    # Instantiate database record
    new_log = models.DailyLog(
        date=payload.date,
        item_id=food_item.id,
        past_sales=payload.past_sales,
        headcount=payload.headcount,
        prep_qty=payload.prep_qty,
        actual_sales=payload.actual_sales,
        leftover_qty=leftover,
        is_weekend=payload.is_weekend,
        is_rainy=payload.is_rainy,
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return DailyLogResponse(
        id=new_log.id,
        date=str(new_log.date),
        item_name=food_item.name,
        past_sales=new_log.past_sales,
        headcount=new_log.headcount,
        prep_qty=new_log.prep_qty,
        actual_sales=new_log.actual_sales,
        leftover_qty=new_log.leftover_qty,
        is_weekend=new_log.is_weekend,
        is_rainy=new_log.is_rainy,
    )