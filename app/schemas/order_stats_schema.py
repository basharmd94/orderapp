from pydantic import BaseModel
from typing import List
from datetime import date

class MonthlyOrderStats(BaseModel):
    month: int
    year: int
    total_orders: int
    total_amount: float
    
class YearlyOrderStats(BaseModel):
    monthly_stats: List[MonthlyOrderStats]
    total_orders: int
    total_amount: float
    pending_orders: int
    completed_orders: int

    class Config:
        from_attributes = True