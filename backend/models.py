# backend/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, default="Main Course")
    unit = Column(String, default="plates")
    cost_per_unit_inr = Column(Float, default=50.0)

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    item_id = Column(Integer, ForeignKey("food_items.id"))
    past_sales = Column(Integer, nullable=False)
    headcount = Column(Integer, nullable=False)
    prep_qty = Column(Integer, nullable=False)
    actual_sales = Column(Integer, nullable=True)
    leftover_qty = Column(Integer, nullable=True)
    is_weekend = Column(Boolean, default=False)
    is_rainy = Column(Boolean, default=False)

    item = relationship("FoodItem")