import os
import random
import datetime
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "canteen_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "rf_model.pkl")

def generate_and_train():
    print("Generating synthetic canteen dataset...")
    random.seed(42)
    np.random.seed(42)

    rows = []
    items = ["Chicken Rice", "Veg Biryani", "Medu Vada"]
    
    for i in range(500):
        item = random.choice(items)
        headcount = random.randint(200, 450)
        past_sales = random.randint(100, 220)
        prep_qty = past_sales + random.randint(10, 30)
        is_weekend = random.choice([0, 1])
        is_rainy = random.choice([0, 1])

        # Target formula with slight random noise
        demand = past_sales + (headcount * 0.15) - (is_rainy * 10) + (is_weekend * 15)
        demand = max(50, int(demand + np.random.normal(0, 5)))

        rows.append({
            "item_name": item,
            "past_sales": past_sales,
            "headcount": headcount,
            "prep_qty": prep_qty,
            "is_weekend": is_weekend,
            "is_rainy": is_rainy,
            "demand": demand
        })

    df = pd.DataFrame(rows)
    df.to_csv(CSV_PATH, index=False)
    print(f"Saved dataset to {CSV_PATH}")

    # Train Model
    X = df[["past_sales", "headcount", "prep_qty", "is_weekend", "is_rainy"]]
    y = df["demand"]

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    joblib.dump(rf, MODEL_PATH)
    print(f"Model successfully trained and saved to {MODEL_PATH}")

if __name__ == "__main__":
    generate_and_train()