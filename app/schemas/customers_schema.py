from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

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
    xtitle: Optional[str] = None  # Customer segment title
    xfax: Optional[str] = None  # Customer segmentation score (0.0 to 1.0)
    xcreditr: Optional[str] = None  # Offer details

    class Config:
        from_attributes = True

class SalesmanAreaRequest(BaseModel):
    """Request schema for getting salesman by area"""
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
    """Response schema for salesman area information"""
    xsp: Optional[str] = None
    xsp1: Optional[str] = None
    xsp2: Optional[str] = None
    xsp3: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "xsp": "SA--000001",
                "xsp1": "SA--000002",
                "xsp2": "SA--000003",
                "xsp3": "SA--000004"
            }
        }

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



segment_map = {
    "0.0-0.1": "Critical Watch",
    "0.1-0.2": "High Risk",
    "0.2-0.3": "Warning Zone",
    "0.3-0.4": "Needs Attention",
    "0.4-0.5": "Developing",
    "0.5-0.6": "Stable",
    "0.6-0.7": "Solid Performer",
    "0.7-0.8": "Valued Partner",
    "0.8-0.9": "Top Tier",
    "0.9-1.0": "Elite Champion"
}

class CustomerSegment(str, Enum):
    CRITICAL_WATCH = "Critical Watch"
    HIGH_RISK = "High Risk"
    WARNING_ZONE = "Warning Zone"
    NEEDS_ATTENTION = "Needs Attention"
    DEVELOPING = "Developing"
    STABLE = "Stable"
    SOLID_PERFORMER = "Solid Performer"
    VALUED_PARTNER = "Valued Partner"
    TOP_TIER = "Top Tier"
    ELITE_CHAMPION = "Elite Champion"
 
class CustomerOfferSchema(BaseModel):
    """
    Schema for customer Offer data.
    - **zid**: Unique customer ID
    - **xtitle**: Customer segment title (e.g., "Developing-1")
    - **xcreditr**: Default offer for the customer
    - **xmonper**: Extra sales percentage based on segmentation
    - **xmondiscper**: Discount percentage based on segmentation
    - **xisgotmon**: Whether the customer got monitoring offer ('True'/'False')
    - **xisgotdefault**: Whether the customer got default offer ('True'/'False')
    """
    zid: int
    xtitle: CustomerSegment  # Customer's segment title as enum
    xcreditr: Optional[str] = None  # What offer the customer is eligible for
    xmonper: Optional[int] = None  # Extra sales percentage based on segmentation
    xmondiscper: Optional[int] = None  # Discount percentage based on segmentation
    xisgotmon: Optional[str] = 'false' # Whether the customer got monitoring offer
    xisgotdefault: Optional[str] = 'false' # Whether the customer got default offer
 
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "xtitle": "Developing",
                "xcreditr": "Free Tshirt",
                "xmonper": 10,
                "xmondiscper": 5,
                "xisgotmon": 'false',
                "xisgotdefault": 'false'
            }
        }
        schema_extra = {
            "openapi_schema": {
                "properties": {
                    "xtitle": {
                        "title": "Customer Segment",
                        "type": "string",
                        "enum": [
                            "Critical Watch",
                            "High Risk", 
                            "Warning Zone",
                            "Needs Attention",
                            "Developing",
                            "Stable",
                            "Solid Performer",
                            "Valued Partner",
                            "Top Tier",
                            "Elite Champion"
                        ],
                        "description": "Select customer segment to apply the offer"
                    }
                }
            }
        }
 
class CustomerDetailSchema(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    net_yearly_purchase: float
    net_monthly_purchase: float
    target: float
    gap: float
    is_eligible_for_offer: bool
    offer: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "segment": "Solid Performer"
            }
        }

class IsGotDefaultOfferSchema(BaseModel):
    zid: int
    xcus: str

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "zid": 100001,
                "xcus": "CUS-00001"
            }
        }

class IsGotMonitoringOfferSchema(BaseModel):
    zid: int
    xcus: str

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "zid": 100001,
                "xcus": "CUS-001581"
            }
        }