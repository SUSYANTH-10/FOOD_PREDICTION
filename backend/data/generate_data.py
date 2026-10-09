import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducible statistical results
np.random.seed(42)

def generate_canteen_dataset(num_records=500):
    start_date = datetime(2025, 1, 1)
    
    dishes = [
        {"name": "Chicken Rice", "base_price": 100, "co2_factor": 0.85},
        {"name": "Veg Biryani", "base_price": 80, "co2_factor": 0.45},
        {"name": "Medu Vada", "base_price": 30, "co2_factor": 0.20}
    ]
    
    records = []
    
    for i in range(num_records):
        current_date = start_date + timedelta(days=i)
        
        is_weekend = 1 if current_date.weekday() >= 5 else 0
        is_rainy = 1 if np.random.rand() < 0.20 else 0
        
        if is_weekend:
            headcount = int(np.random.normal(180, 30))
        else:
            headcount = int(np.random.normal(450, 50))
            
        dish = np.random.choice(dishes)
        past_sales = int(headcount * np.random.uniform(0.35, 0.45))
        
        base_demand = headcount * 0.40
        if is_rainy:
            base_demand *= 1.10
        if is_weekend:
            base_demand *= 0.75
            
        actual_demand = max(10, int(base_demand + np.random.normal(0, 8)))
        
        records.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "item_name": dish["name"],
            "past_sales": past_sales,
            "headcount": headcount,
            "is_weekend": is_weekend,
            "is_rainy": is_rainy,
            "actual_demand": actual_demand
        })
        
    df = pd.DataFrame(records)
    # Saves directly into the backend directory
    df.to_csv("../canteen_data.csv", index=False)
    print(f"✅ Generated {len(df)} records in 'canteen_data.csv'")

if __name__ == "__main__":
    generate_canteen_dataset()