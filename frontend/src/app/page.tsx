"use client";

import { useState, useEffect } from "react";

interface PredictionData {
  item_name: string;
  unit: string;
  predicted_demand: number;
  recommended_prep: number;
  surplus_qty: number;
  unit_price: number;
  financial_risk_inr: number;
  carbon_risk_kg: number;
  xai_reasoning: string;
}

const MENU_OPTIONS = [
  "Chicken Rice",
  "Egg Rice",
  "Special Meals",
  "Veg Biryani",
  "Medu Vada (2 pcs)"
];

const DISH_IMAGES: Record<string, string> = {
  "Chicken Rice": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?q=80&w=1920&auto=format&fit=crop",
  "Egg Rice": "https://images.unsplash.com/photo-1512058564366-18510be2db19?q=80&w=1920&auto=format&fit=crop",
  "Special Meals": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?q=80&w=1920&auto=format&fit=crop",
  "Veg Biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?q=80&w=1920&auto=format&fit=crop",
  "Medu Vada (2 pcs)": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?q=80&w=1920&auto=format&fit=crop"
};

export default function CanteenDashboard() {
  const [selectedDish, setSelectedDish] = useState<string>("Chicken Rice");
  const [pastSales, setPastSales] = useState<number>(150);
  const [headcount, setHeadcount] = useState<number>(300);
  const [prepQty, setPrepQty] = useState<number>(180);
  const [isWeekend, setIsWeekend] = useState<boolean>(false);
  const [isRainy, setIsRainy] = useState<boolean>(false);

  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDemandAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch("http://localhost:8000/api/v1/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            item_name: selectedDish,
            past_sales: Number(pastSales),
            headcount: Number(headcount),
            prep_qty: Number(prepQty),
            is_weekend: isWeekend,
            is_rainy: isRainy,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to calculate prediction metrics.");
        }

        const data: PredictionData = await response.json();
        setPrediction(data);
      } catch (err: any) {
        setError(err.message || "Connection to microservice failed.");
      } finally {
        setLoading(false);
      }
    };

    fetchDemandAnalytics();
  }, [selectedDish, pastSales, headcount, prepQty, isWeekend, isRainy]);

  const currentBgImage = DISH_IMAGES[selectedDish] || DISH_IMAGES["Chicken Rice"];

  return (
    <main 
      className="min-h-screen text-slate-900 relative bg-cover bg-center bg-no-repeat transition-all duration-700 ease-in-out font-sans"
      style={{ backgroundImage: `url('${currentBgImage}')` }}
    >
      {/* Lightly Dimmed Translucent Overlay (40% Dark Slate + Blur) */}
      <div className="min-h-screen w-full bg-slate-900/40 backdrop-blur-md p-6 md:p-12">
        
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Header */}
          <header className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-white/30 pb-6 gap-4">
            <div>
              <h1 className="text-3xl font-black text-white drop-shadow-md">
                AI Demand & Waste Analytics
              </h1>
              <p className="text-slate-100 text-sm font-medium mt-1 drop-shadow-sm">
                Real-time predictive kitchen capacity and environmental impact optimizer
              </p>
            </div>
            <div className="flex items-center gap-2 bg-white/80 border border-slate-200/80 px-4 py-2 rounded-full text-xs font-bold text-slate-900 shadow-md backdrop-blur-md">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              FastAPI Microservice Connected
            </div>
          </header>

          {/* Dashboard Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Controls Card */}
            <div className="lg:col-span-5 bg-white/80 backdrop-blur-xl border border-slate-200/90 p-6 rounded-2xl space-y-6 shadow-2xl">
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                🍽️ Kitchen Parameters
              </h2>

              {/* Dish Dropdown */}
              <div>
                <label className="block text-xs font-extrabold text-slate-700 mb-2 uppercase tracking-wider">
                  Select Dish
                </label>
                <select
                  value={selectedDish}
                  onChange={(e) => setSelectedDish(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500 transition shadow-sm"
                >
                  {MENU_OPTIONS.map((dish) => (
                    <option key={dish} value={dish} className="bg-white text-slate-900">
                      {dish}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sliders & Inputs */}
              <div className="space-y-5">
                <div>
                  <div className="flex justify-between text-xs font-bold text-slate-700 mb-2">
                    <span>Expected Headcount</span>
                    <span className="font-extrabold text-emerald-700">{headcount} students</span>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="1000"
                    step="10"
                    value={headcount}
                    onChange={(e) => setHeadcount(Number(e.target.value))}
                    className="w-full accent-emerald-600 bg-slate-200 h-2 rounded-lg cursor-pointer"
                  />
                </div>

                <div>
                  <div className="flex justify-between text-xs font-bold text-slate-700 mb-2">
                    <span>Planned Prep Quantity</span>
                    <span className="font-extrabold text-emerald-700">{prepQty} portions</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="500"
                    step="5"
                    value={prepQty}
                    onChange={(e) => setPrepQty(Number(e.target.value))}
                    className="w-full accent-emerald-600 bg-slate-200 h-2 rounded-lg cursor-pointer"
                  />
                </div>

                <div>
                  <label className="block text-xs font-extrabold text-slate-700 mb-2 uppercase tracking-wider">
                    Past Sales Reference
                  </label>
                  <input
                    type="number"
                    value={pastSales}
                    onChange={(e) => setPastSales(Number(e.target.value))}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-slate-900 font-bold focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
                  />
                </div>
              </div>

              {/* Weather & Day Toggles */}
              <div className="grid grid-cols-2 gap-4 pt-2">
                <button
                  type="button"
                  onClick={() => setIsRainy(!isRainy)}
                  className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-bold transition shadow-sm ${
                    isRainy 
                      ? "bg-blue-100 border-blue-400 text-blue-900" 
                      : "bg-slate-50 border-slate-300 text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {isRainy ? "🌧️ Rainy Weather" : "☀️ Clear Weather"}
                </button>

                <button
                  type="button"
                  onClick={() => setIsWeekend(!isWeekend)}
                  className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-bold transition shadow-sm ${
                    isWeekend 
                      ? "bg-amber-100 border-amber-400 text-amber-900" 
                      : "bg-slate-50 border-slate-300 text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {isWeekend ? "📅 Weekend" : "📆 Weekday"}
                </button>
              </div>
            </div>

            {/* Right Metrics Display */}
            <div className="lg:col-span-7 space-y-6">
              
              {loading && (
                <div className="flex items-center justify-center p-12 bg-white/80 backdrop-blur-xl border border-slate-200/90 rounded-2xl text-slate-800 font-bold gap-3 shadow-2xl">
                  <div className="w-5 h-5 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
                  Computing model metrics...
                </div>
              )}

              {error && (
                <div className="p-4 bg-red-100/90 backdrop-blur-xl border border-red-300 rounded-2xl text-red-900 text-sm font-bold flex items-center gap-2 shadow-lg">
                  ⚠️ {error}
                </div>
              )}

              {prediction && !loading && (
                <>
                  {/* Metric Cards Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-white/85 backdrop-blur-xl border border-slate-200/90 p-5 rounded-2xl space-y-1 shadow-xl">
                      <div className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                        📈 Predicted Demand
                      </div>
                      <div className="text-3xl font-extrabold text-slate-900">
                        {prediction.predicted_demand} <span className="text-xs text-slate-500 font-normal">{prediction.unit}</span>
                      </div>
                      <div className="text-xs text-emerald-700 font-bold">
                        Rec. Prep (+5% buffer): <span>{prediction.recommended_prep}</span>
                      </div>
                    </div>

                    <div className="bg-white/85 backdrop-blur-xl border border-slate-200/90 p-5 rounded-2xl space-y-1 shadow-xl">
                      <div className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                        ⚠️ Surplus Margin
                      </div>
                      <div className={`text-3xl font-extrabold ${prediction.surplus_qty > 0 ? "text-amber-600" : "text-emerald-600"}`}>
                        {prediction.surplus_qty > 0 ? `+${prediction.surplus_qty}` : prediction.surplus_qty}
                        <span className="text-xs text-slate-500 font-normal"> {prediction.unit}</span>
                      </div>
                      <div className="text-xs text-slate-600 font-semibold">
                        Unit price: ₹{prediction.unit_price}
                      </div>
                    </div>

                    <div className="bg-white/85 backdrop-blur-xl border border-slate-200/90 p-5 rounded-2xl space-y-1 shadow-xl">
                      <div className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                        💰 Financial Capital Risk
                      </div>
                      <div className="text-3xl font-extrabold text-slate-900">
                        ₹{prediction.financial_risk_inr.toLocaleString("en-IN")}
                      </div>
                      <div className="text-xs text-slate-600 font-semibold">Potential direct capital loss</div>
                    </div>

                    <div className="bg-white/85 backdrop-blur-xl border border-slate-200/90 p-5 rounded-2xl space-y-1 shadow-xl">
                      <div className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                        🌱 Wasted Carbon Footprint
                      </div>
                      <div className="text-3xl font-extrabold text-emerald-700">
                        {prediction.carbon_risk_kg} <span className="text-xs font-normal text-slate-600">kg CO₂e</span>
                      </div>
                      <div className="text-xs text-slate-600 font-semibold">Embodied lifecycle emissions</div>
                    </div>
                  </div>

                  {/* Explainable AI Reasoning Box */}
                  <div className="bg-white/85 backdrop-blur-xl border border-slate-200/90 p-6 rounded-2xl space-y-2 shadow-xl">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-emerald-800">
                      Explainable AI Insight
                    </h3>
                    <p className="text-sm text-slate-800 font-bold leading-relaxed">
                      {prediction.xai_reasoning}
                    </p>
                  </div>
                </>
              )}
            </div>

          </div>
        </div>

      </div>
    </main>
  );
}