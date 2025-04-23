from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Pydantic model for API request validation
class LocationCreate(BaseModel):
    """Schema for creating a new location record."""
    username: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    
    name: Optional[str] = None
    street: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    formatted_address: Optional[str] = None
    maps_url: Optional[str] = None
    timestamp: datetime
    business_id: Optional[int] = None
    notes: Optional[str] = None
    device_info: Optional[str] = None
    is_check_in: Optional[bool] = False
    shared_via: Optional[str] = None

# Pydantic model for API response
class Location(LocationCreate):
    """Schema for location response, extends create schema with id and created_at."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Model for querying locations
class LocationQuery(BaseModel):
    """Schema for querying location records with filters."""
    username: Optional[str] = None
    business_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0
