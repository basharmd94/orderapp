from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderSummaryResponse(BaseModel):
    """Response schema for order summary data"""
    zid: int
    invoiceno: str
    xcus: str
    xcusname: str
    items: str
    total_qty: int
    total_price: float
    total_linetotal: float
    xstatusord: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "invoiceno": "T001-INV-12345",
                "xcus": "CUS-000001",
                "xcusname": "Fixit Gulshan",
                "items": "CF000001 - Draino Powder, CF000002 - Clean x 1 litre",
                "total_qty": 15,
                "total_price": 1500.0,
                "total_linetotal": 1500.0,
                "xstatusord": "New"
            }
        }


class OrderSummaryListResponse(BaseModel):
    """Response schema for list of order summaries"""
    orders: List[OrderSummaryResponse]
    count: int = Field(..., description="Total number of orders")
    status: str = Field(..., description="Order status")

    class Config:
        json_schema_extra = {
            "example": {
                "orders": [
                    {
                        "zid": 100001,
                        "invoiceno": "T001-INV-12345",
                        "xcus": "CUS-000001",
                        "xcusname": "Fixit Gulshan",
                        "items": "CF000001 - Draino Powder, CF000002 - Clean x 1 litre",
                        "total_qty": 15,
                        "total_price": 1500.0,
                        "total_linetotal": 1500.0,
                        "xstatusord": "New"
                    }
                ],
                "count": 1,
                "status": "New"
            }
        }
