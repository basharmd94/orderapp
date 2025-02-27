from pydantic import BaseModel
from typing import List, Optional

class CustomersSchema(BaseModel):
    zid: int
    xcus: str
    xorg: str
    xadd1: str
    xcity: str
    xstate: str
    xmobile: str
    xtaxnum: str
    xsp: Optional[str] = None
    xsp1: Optional[str] = None
    xsp2: Optional[str] = None
    xsp3: Optional[str] = None

    class Config:
        from_attributes = True

class SalesmanAreaRequest(BaseModel):
    zid: int
    area: str

    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "area": "Uttora"
            }
        }

class SalesmanAreaResponse(BaseModel):
    xsp: str | None = None
    xsp1: str | None = None
    xsp2: str | None = None
    xsp3: str | None = None

    class Config:
        from_attributes = True

class SalesmanAreaUpdateRequest(BaseModel):
    zid: int
    area: str
    xsp: Optional[str] = None
    xsp1: Optional[str] = None
    xsp2: Optional[str] = None
    xsp3: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "area": "Uttora",
                "xsp": "SA--000001",
                "xsp1": "SA--000002",
                "xsp2": "SA--000003",
                "xsp3": "SA--000004"
            }
        }

class SalesmanUpdateResponse(BaseModel):
    message: str
    updated_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Successfully updated salesman assignments",
                "updated_count": 5
            }
        }

class AreaByZidRequest(BaseModel):
    zid: int
    user_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "user_id": "SA--000001"  # Optional
            }
        }

class AreaResponse(BaseModel):
    areas: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "areas": ["Uttora", "Gulshan", "Banani"]
            }
        }

