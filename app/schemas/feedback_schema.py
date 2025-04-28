from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    """Base schema for feedback with common fields."""
    zid: int = Field(..., description="Business ID")
    is_delivery_issue: bool = Field(default=False, description="Whether there's a delivery issue")
    is_collection_issue: bool = Field(default=False, description="Whether there's a collection issue")
    description: str = Field(..., description="Detailed feedback description (can be in Bangla)")
    
    class Config:
        from_attributes = True

class FeedbackCreate(FeedbackBase):
    """Schema for creating new feedback."""
    customer_ids: List[str] = Field(..., description="List of customer IDs associated with the feedback")
    product_ids: List[str] = Field(..., description="List of product IDs associated with the feedback")
    user_id: Optional[str] = Field(None, description="User ID associated with the feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "zid": 100001,
                "customer_ids": ["CUS-000001", "CUS-000002"],
                "product_ids": ["CF000001", "CF000002"],
                "is_delivery_issue": True,
                "is_collection_issue": False,
                "description": "পণ্যটি ভালো ছিল কিন্তু প্যাকেজিং ক্ষতিগ্রস্ত হয়েছে",
                "user_id": "IT--000010"
            }
        }

class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    id: int
    translated_desc: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: str
    user_id: Optional[str] = None
    customer_ids: List[str]
    product_ids: List[str]
    
    class Config:
        from_attributes = True

class FeedbackQuery(BaseModel):
    """Schema for querying feedback with filters."""
    zid: Optional[int] = None
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    is_delivery_issue: Optional[bool] = None
    is_collection_issue: Optional[bool] = None
    created_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0