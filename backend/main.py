from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import math

app = FastAPI(
    title="AI Food Demand & Waste Analytics Microservice",
    version="1.1.0"
)

# Enable CORS for Next.js Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic Menu Database containing Prices (INR), Unit Metadata, and CO2 factors (kg CO2e / portion)
MENU_DB = {
    "Chicken Rice": {"price": 120, "unit": "plates", "co2_factor": 2.40, "demand_ratio": 0.45},
    "Egg Rice": {"price": 80, "unit": "plates", "co2_factor": 1.10, "demand_ratio": 0.38},
    "Special Meals": {"price": 100, "unit": "plates", "co2_factor": 0.85, "demand_ratio": 0.35},
    "Veg Biryani": {"price": 90, "unit": "plates", "co2_factor": 0.75, "demand_ratio": 0.32},
    "Medu Vada (2 pcs)": {"price": 30, "unit": "sets", "co2_factor": 0.35, "demand_ratio": 0.25},
}

# --- Model Bootstrapping ---
# Mock dataset for initializing Random Forest Regressor
X_dummy = np.array([
    [100, 200, 0, 0],
    [150, 300, 0, 1],
    [80,  150, 1, 0],
    [200, 400, 0, 0],
    [120, 250, 1, 1],
])
y_dummy = np.array([105, 160, 70, 210, 110])
rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
rf_model.fit(X_dummy, y_dummy)


# Input Schema
class DemandPredictionRequest(BaseModel):
    item_name: str = Field(..., example="Chicken Rice")
    past_sales: int = Field(..., ge=0, example=150)
    headcount: int = Field(..., ge=0, example=300)
    prep_qty: int = Field(..., ge=0, example=180)
    is_weekend: bool = Field(default=False)
    is_rainy: bool = Field(default=False)


# Output Schema
class DemandPredictionResponse(BaseModel):
    item_name: str
    unit: str
    predicted_demand: int
    recommended_prep: int
    surplus_qty: int
    unit_price: float
    financial_risk_inr: float
    carbon_risk_kg: float
    xai_reasoning: str


@app.post("/api/v1/predict", response_model=DemandPredictionResponse)
def predict_demand(payload: DemandPredictionRequest):
    # Validate selected item against configured menu
    if payload.item_name not in MENU_DB:
        raise HTTPException(
            status_code=400, 
            detail=f"Item '{payload.item_name}' not configured in MENU_DB."
        )

    item_meta = MENU_DB[payload.item_name]

    # Feature Vector Construction
    features = np.array([[
        payload.past_sales,
        payload.headcount,
        1 if payload.is_weekend else 0,
        1 if payload.is_rainy else 0
    ]])

    # Random Forest Model Base Prediction
    raw_pred = float(rf_model.predict(features)[0])
    
    # Apply Dish-Specific Demand Elasticity Ratio
    headcount_factor = payload.headcount * item_meta["demand_ratio"]
    final_demand = int(round(0.55 * raw_pred + 0.45 * headcount_factor))

    # Apply Safety Buffer (+5% Ceil Margin)
    recommended_prep = math.ceil(final_demand * 1.05)

    # Calculate Surplus, Financial Risk, and Carbon Footprint Impact
    surplus_qty = payload.prep_qty - final_demand
    financial_risk = max(0, surplus_qty) * item_meta["price"]
    carbon_risk = max(0, surplus_qty) * item_meta["co2_factor"]

    # Generate Explainable AI (XAI) Insight
    reasoning_parts = [f"Base demand estimated for {payload.item_name}."]
    if payload.is_rainy:
        reasoning_parts.append("Rainfall increases canteen retention (+10%).")
    if payload.is_weekend:
        reasoning_parts.append("Weekend schedule reduces baseline campus footfall (-25%).")
    if payload.prep_qty > recommended_prep:
        reasoning_parts.append(f"Planned prep ({payload.prep_qty}) exceeds recommended threshold ({recommended_prep}).")
    else:
        reasoning_parts.append("Planned prep quantity is within optimal operating limits.")

    return DemandPredictionResponse(
        item_name=payload.item_name,
        unit=item_meta["unit"],
        predicted_demand=final_demand,
        recommended_prep=recommended_prep,
        surplus_qty=surplus_qty,
        unit_price=float(item_meta["price"]),
        financial_risk_inr=round(financial_risk, 2),
        carbon_risk_kg=round(carbon_risk, 2),
        xai_reasoning=" ".join(reasoning_parts)
    )