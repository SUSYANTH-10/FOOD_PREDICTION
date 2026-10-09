import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_canteen_model():
    csv_path = "canteen_data.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: '{csv_path}' not found! Run generate_data.py first.")
        return

    print("📥 Loading dataset from canteen_data.csv...")
    df = pd.read_csv(csv_path)

    # 1. Select the 4D Feature Vector (X) and Target (y)
    X = df[["past_sales", "headcount", "is_weekend", "is_rainy"]]
    y = df["actual_demand"]

    # 2. Perform an 80/20 Train-Test Split with a fixed random_state for reproducibility
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    print(f"📊 Dataset split: {len(X_train)} training records | {len(X_test)} test records.")

    # 3. Instantiate and train the RandomForestRegressor
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        random_state=42
    )
    
    print("⏳ Training Random Forest Regressor...")
    rf.fit(X_train, y_train)

    # 4. Predict on the unseen 20% test holdout set
    y_pred = rf.predict(X_test)

    # 5. Compute statistical metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n" + "=" * 45)
    print("🎯 TEST SET EVALUATION METRICS:")
    print("=" * 45)
    print(f"  • MAE  (Mean Absolute Error) : {mae:.2f} plates")
    print(f"  • RMSE (Root Mean Sq Error)  : {rmse:.2f} plates")
    print(f"  • R² Score (Variance Ratio)  : {r2:.4f}")
    print("=" * 45)

    # 6. Save the trained model binary
    model_output_path = "rf_model.pkl"
    joblib.dump(rf, model_output_path)
    print(f"\n✅ Model successfully trained and saved to '{model_output_path}'!")

if __name__ == "__main__":
    train_canteen_model()