from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from datetime import datetime

class CustomerBalanceRequest(BaseModel):
    zid: int = Field(..., description="Business ID")
    customer: str = Field(..., description="Customer ID")
    frm_date: date = Field(..., description="From Date (YYYY-MM-DD)")
    to_date: Optional[date] = Field(None, description="To Date (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "customer": "CUS-000002",
                "frm_date": "2024-04-22",
                "to_date": "2025-04-22"
            }
        }

class LedgerEntry(BaseModel):
    transaction_date: date
    entry_type: str
    amount: float
    voucher: str
    running_balance: float

class CustomerBalanceResponse(BaseModel):
    customer_id: str
    from_date: date
    to_date: date
    opening_balance: float
    closing_balance: float
    ledger_entries: List[LedgerEntry]
    total_entries: int
