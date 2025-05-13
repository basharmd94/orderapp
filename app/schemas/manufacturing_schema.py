from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ManufacturingOrderSchema(BaseModel):
    """Schema for Manufacturing Order (MO) data."""
    zid: int
    xdate: Optional[date] = None
    xmoord: str
    xitem: str
    xdesc: Optional[str] = None
    xqtyprd: float
    xunit: Optional[str] = None
    stock: Optional[float] = None
    last_mo_qty: Optional[float] = None
    last_mo_date: Optional[date] = None
    last_mo_number: Optional[str] = None
    mo_cost: Optional[float] = None

    class Config:
        from_attributes = True

class ManufacturingOrderListResponse(BaseModel):
    """Response schema for a list of Manufacturing Orders with pagination details."""
    items: List[ManufacturingOrderSchema]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "zid": 100000,
                        "xdate": "2025-05-01",
                        "xmoord": "MO-2025-001",
                        "xitem": "ITEM1",
                        "xdesc": "Product Description",                        "xqtyprd": 100.0,
                        "xunit": "PCS",
                        "stock": 250.0,
                        "last_mo_qty": 75.0,
                        "last_mo_date": "2025-04-15",
                        "last_mo_number": "MO-2025-0890",
                        "mo_cost": 125.50
                    }
                ],
                "total": 45,
                "page": 1,
                "size": 10,
                "pages": 5
            }
        }

class ManufacturingOrderRequest(BaseModel):
    """Request schema for filtering Manufacturing Orders."""
    zid: int
    search_text: Optional[str] = None
    page: int = 1
    size: int = 10

    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100000,
                "search_text": "ITEM1",
                "page": 1,
                "size": 10
            }
        }

class ManufacturingOrderDetailSchema(BaseModel):
    """Schema for Manufacturing Order Detail data."""
    xitem: str
    xdesc: Optional[str] = None
    xunit: Optional[str] = None
    raw_qty: float
    rate: float
    total_amt: float
    cost_per_item: float
    stock: float

    class Config:
        from_attributes = True

# Use List directly as the response model for MO details
# This will return a pure list without wrapping it in an "items" field
class ManufacturingOrderDetailList(List[ManufacturingOrderDetailSchema]):
    """Response schema for a list of Manufacturing Order Details."""
    
    # This class extends List[ManufacturingOrderDetailSchema] so it will serialize as a pure JSON array

    class Config:
        json_schema_extra = {
            "example": [
                {
                    "xitem": "RAW-001",
                    "xdesc": "Raw Material A",
                    "xunit": "KG",
                    "raw_qty": 10.5,
                    "rate": 25.75,
                    "total_amt": 270.38,
                    "cost_per_item": 2.70,
                    "stock": 450.0
                }
            ]
        }
