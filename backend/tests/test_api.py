import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

# 1. Test Valid API Endpoint Request & Core Schema Output
def test_predict_success_endpoint():
    payload = {
        "item_name": "Chicken Rice",
        "past_sales": 150,
        "headcount": 350,
        "prep_qty": 180,
        "is_weekend": False,
        "is_rainy": True
    }
    response = client.post("/api/v1/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert core properties present in main.py response
    assert "item_name" in data
    assert "predicted_demand" in data
    assert "recommended_prep" in data
    assert "unit" in data

# 2. Test 5% Safety Buffer Heuristic
def test_safety_buffer_rule():
    payload = {
        "item_name": "Veg Biryani",
        "past_sales": 100,
        "headcount": 250,
        "prep_qty": 120,
        "is_weekend": False,
        "is_rainy": False
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Recommended prep must include safety buffer above predicted demand
    assert data["recommended_prep"] >= data["predicted_demand"]

# 3. Test Machine Learning Inference Execution
def test_ml_model_inference_execution():
    payload = {
        "item_name": "Chicken Rice",
        "past_sales": 120,
        "headcount": 300,
        "prep_qty": 150,
        "is_weekend": False,
        "is_rainy": False
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data["predicted_demand"], int)
    assert data["predicted_demand"] > 0

# 4. Test Pydantic Schema Validation Failure
def test_pydantic_invalid_type_validation():
    payload = {
        "item_name": "Chicken Rice",
        "past_sales": "invalid_text_value",
        "headcount": 300,
        "prep_qty": 150,
        "is_weekend": False,
        "is_rainy": False
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

## 5. Test Non-Negative Metric Output Values
# 5. Test Non-Negative Metric Output Values
def test_non_negative_risk_outputs():
    payload = {
        "item_name": "Chicken Rice",
        "past_sales": 150,
        "headcount": 350,
        "prep_qty": 250,
        "is_weekend": False,
        "is_rainy": True
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Ensure numerical outputs are non-negative
    assert data["predicted_demand"] >= 0
    assert data["recommended_prep"] >= 0