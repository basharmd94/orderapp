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
                        "xdesc": "Product Description",
                        "xqtyprd": 100.0,
                        "xunit": "PCS",
                        "stock": 250.0,
                        "last_mo_qty": 75.0,
                        "last_mo_date": "2025-04-15",
                        "last_mo_number": "MO-2025-0890"
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
