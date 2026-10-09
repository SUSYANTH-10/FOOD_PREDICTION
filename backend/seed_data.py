# backend/seed_data.py
import os
import random
import datetime
import pandas as pd
from database import engine, SessionLocal, Base
from models import FoodItem, DailyLog

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Reset existing records
    db.query(DailyLog).delete()
    db.query(FoodItem).delete()
    db.commit()

    # 1. Populate default food catalog
    items = [
        FoodItem(name="Chicken Rice", category="Non-Veg", cost_per_unit_inr=100.0),
        FoodItem(name="Veg Biryani", category="Veg", cost_per_unit_inr=70.0),
        FoodItem(name="Medu Vada", category="Snacks", cost_per_unit_inr=30.0),
    ]
    db.add_all(items)
    db.commit()

    item_map = {item.name: item.id for item in db.query(FoodItem).all()}

    # 2. Check if generated CSV exists, otherwise synthesize 500 records dynamically
    csv_path = os.path.join(os.path.dirname(__file__), "food_demand_data.csv")
    
    today = datetime.date.today()
    logs_to_insert = []

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            item_name = row.get("item_name", "Chicken Rice")
            item_id = item_map.get(item_name, item_map["Chicken Rice"])
            
            past_sales = int(row["past_sales"])
            prep_qty = int(row["prep_qty"])
            actual_sales = min(prep_qty, past_sales + random.randint(-5, 10))
            leftovers = max(0, prep_qty - actual_sales)

            logs_to_insert.append(
                DailyLog(
                    date=today - datetime.timedelta(days=len(logs_to_insert) % 500),
                    item_id=item_id,
                    past_sales=past_sales,
                    headcount=int(row["headcount"]),
                    prep_qty=prep_qty,
                    actual_sales=actual_sales,
                    leftover_qty=leftovers,
                    is_weekend=bool(row["is_weekend"]),
                    is_rainy=bool(row["is_rainy"]),
                )
            )
    else:
        # Fallback generator for 500 records
        for i in range(500, 0, -1):
            log_date = today - datetime.timedelta(days=i)
            item_id = random.choice(list(item_map.values()))
            headcount = random.randint(200, 450)
            past_sales = random.randint(100, 220)
            prep_qty = past_sales + random.randint(10, 30)
            actual_sales = min(prep_qty, past_sales + random.randint(-8, 12))
            leftovers = max(0, prep_qty - actual_sales)

            logs_to_insert.append(
                DailyLog(
                    date=log_date,
                    item_id=item_id,
                    past_sales=past_sales,
                    headcount=headcount,
                    prep_qty=prep_qty,
                    actual_sales=actual_sales,
                    leftover_qty=leftovers,
                    is_weekend=log_date.weekday() >= 5,
                    is_rainy=random.random() < 0.2,
                )
            )

    db.add_all(logs_to_insert)
    db.commit()
    print(f"Database successfully populated with {len(logs_to_insert)} records!")
    db.close()

if __name__ == "__main__":
    seed_database()