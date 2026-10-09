import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION (Next.js / shadcn visual theme)
# ---------------------------------------------------------
st.set_page_config(page_title="Smart Diner AI — Canteen Demand Intelligence", layout="wide")

st.title("🍽️ Smart Canteen AI — Itemized Food Demand Platform")
st.caption("Review II Milestone — Dish-Level Prediction, Financial Loss & Environmental Engine")

# ---------------------------------------------------------
# 1. CANTEEN MENU DATABASE
# ---------------------------------------------------------
MENU_ITEMS = {
    "Idli (2 pcs)": {"cost": 20, "category": "Breakfast", "perishability": "High", "prep_unit": "Portions"},
    "Masala Dosa": {"cost": 50, "category": "Breakfast", "perishability": "Medium", "prep_unit": "Plates"},
    "Poori Sagu": {"cost": 40, "category": "Breakfast", "perishability": "High", "prep_unit": "Plates"},
    "South Indian Meals": {"cost": 80, "category": "Lunch", "perishability": "High", "prep_unit": "Thalis"},
    "Veg Biryani": {"cost": 90, "category": "Lunch", "perishability": "Medium", "prep_unit": "Portions"},
    "Tea / Coffee": {"cost": 15, "category": "Beverage", "perishability": "Low", "prep_unit": "Cups"}
}

# ---------------------------------------------------------
# 2. MULTI-ITEM ML MODEL PIPELINE
# ---------------------------------------------------------
@st.cache_data
def train_menu_model():
    np.random.seed(42)
    n = 600
    
    # Synthetic historical dataset across items
    past_cons = np.random.randint(50, 400, size=n)
    headcount = past_cons + np.random.randint(-20, 60, size=n)
    is_weekend = np.random.choice([0, 1], size=n, p=[0.75, 0.25])
    is_rainy = np.random.choice([0, 1], size=n, p=[0.8, 0.2])
    
    # Target demand
    demand = (headcount * 0.70 + past_cons * 0.20 - is_weekend * 25 + is_rainy * 15 + np.random.normal(0, 10, n)).astype(int)
    
    df = pd.DataFrame({
        'past_consumption': past_cons,
        'expected_people': headcount,
        'is_weekend': is_weekend,
        'is_rainy': is_rainy,
        'demand': demand
    })
    
    X = df[['past_consumption', 'expected_people', 'is_weekend', 'is_rainy']]
    y = df['demand']
    
    model = RandomForestRegressor(n_estimators=40, max_depth=5, random_state=42)
    model.fit(X, y)
    return model

model = train_menu_model()

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS & ITEM SELECTION
# ---------------------------------------------------------
st.sidebar.header("📋 Canteen Operations Control")

selected_item = st.sidebar.selectbox("Select Menu Item", list(MENU_ITEMS.keys()))
item_details = MENU_ITEMS[selected_item]

st.sidebar.info(f"**Category:** {item_details['category']} | **Price:** ₹{item_details['cost']}/portion")

st.sidebar.subheader("📥 Operational Context")
past_sales = st.sidebar.number_input(f"Past Sales for {selected_item} ({item_details['prep_unit']})", 10, 1000, 150)
headcount = st.sidebar.number_input("Expected Hall Headcount", 50, 1500, 300)
prep_qty = st.sidebar.number_input(f"Planned Preparation ({item_details['prep_unit']})", 10, 1000, 180)

st.sidebar.subheader("🌍 Environmental Variables")
day_type = st.sidebar.radio("Day Type", ["Weekday", "Weekend"])
weather = st.sidebar.radio("Weather", ["Clear / Normal", "Rainy / Bad Weather"])

is_weekend = 1 if day_type == "Weekend" else 0
is_rainy = 1 if weather == "Rainy / Bad Weather" else 0

# ---------------------------------------------------------
# 4. PREDICTION & ANALYTICS DASHBOARD
# ---------------------------------------------------------
if st.sidebar.button("Calculate Item Demand & Financial Risk", type="primary"):
    input_df = pd.DataFrame({
        'past_consumption': [past_sales],
        'expected_people': [headcount],
        'is_weekend': [is_weekend],
        'is_rainy': [is_rainy]
    })
    
    pred_demand = float(model.predict(input_df)[0])
    surplus = prep_qty - pred_demand
    financial_loss = max(0, surplus) * item_details['cost']
    co2_emissions = max(0, surplus) * 0.8  # ~0.8 kg CO2e per cooked portion wasted
    
    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"🎯 Predicted Demand", f"{pred_demand:.0f} {item_details['prep_unit']}")
    
    if surplus > 0:
        c2.metric("⚠️ Expected Surplus", f"{surplus:.0f} {item_details['prep_unit']}", delta=f"-{surplus:.0f} Risk", delta_color="inverse")
    else:
        c2.metric("🚨 Shortage Deficit", f"{abs(surplus):.0f} {item_details['prep_unit']}", delta=f"+{abs(surplus):.0f} Needed", delta_color="normal")
        
    c3.metric("💰 Financial Loss Risk", f"₹{financial_loss:,.0f}")
    c4.metric("🌱 Waste Carbon Risk", f"{co2_emissions:.1f} kg CO₂e")
    
    st.markdown("---")
    
    # Tabular Layout
    tab1, tab2, tab3 = st.columns([1, 1, 1])
    
    # Detailed Breakdown Table
    st.subheader("📊 Itemized Decision Summary")
    
    breakdown_data = {
        "Menu Item": [selected_item],
        "Selling Price": [f"₹{item_details['cost']}"],
        "Planned Prep": [f"{prep_qty} {item_details['prep_unit']}"],
        "AI Demand Forecast": [f"{pred_demand:.0f} {item_details['prep_unit']}"],
        "Optimal Prep (+5% Buffer)": [f"{round(pred_demand * 1.05):.0f} {item_details['prep_unit']}"],
        "Perishability Index": [item_details['perishability']],
        "Net Financial Risk": [f"₹{financial_loss:,.0f}"]
    }
    
    st.table(pd.DataFrame(breakdown_data))
    
    # XAI Explanation Box
    st.info(
        f"**Explainable AI (XAI) Drivers:** "
        f"Forecast for **{selected_item}** is **{pred_demand:.0f} portions**. "
        f"Primary factor: Expected hall footfall of **{headcount} people**. "
        f"{'Rainy weather bonus applied (+10% indoor dining boost).' if is_rainy else ''} "
        f"{'Weekend schedule penalty applied.' if is_weekend else ''}"
    )
    
    # Visual gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = prep_qty,
        delta = {'reference': pred_demand},
        title = {'text': f"Planned Prep vs Predicted Demand ({item_details['prep_unit']})"},
        gauge = {
            'axis': {'range': [None, max(prep_qty, pred_demand) * 1.3]},
            'bar': {'color': "#2563eb"},
            'threshold': {'line': {'color': "#dc2626", 'width': 4}, 'value': pred_demand}
        }
    ))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Select a menu item from the sidebar and click **'Calculate Item Demand & Financial Risk'**.")