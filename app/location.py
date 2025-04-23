from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Model for database table
class LocationRecord(Base):
    __tablename__ = "location_records"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # Foreign key to users table
    
    # Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    
    # Address details (from reverse geocoding)
    name = Column(String, nullable=True)
    street = Column(String, nullable=True)
    district = Column(String, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Formatted address (combined address string)
    formatted_address = Column(Text, nullable=True)
    
    # Maps URL
    maps_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    timestamp = Column(DateTime, nullable=False)  # Actual timestamp from device
    
    # Optional metadata
    business_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    device_info = Column(String, nullable=True)
    
    # For tracking check-ins or location sharing events
    is_check_in = Column(Boolean, default=False)
    shared_via = Column(String, nullable=True)  # e.g., "WhatsApp", "Other"

# Pydantic model for API request validation
class LocationCreate(BaseModel):
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
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Optional: Model for querying locations
class LocationQuery(BaseModel):
    username: Optional[str] = None
    business_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0 