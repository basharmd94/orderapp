from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base

class LocationRecord(Base):
    """Model for storing location data in the database."""
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
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Actual timestamp from device
    xdate = Column(String, nullable=True)  # Date in yyyy-mm-dd format for easier querying
    
    # Optional metadata
    business_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    device_info = Column(String, nullable=True)
    
    # For tracking check-ins or location sharing events
    is_check_in = Column(Boolean, default=False)
    shared_via = Column(String, nullable=True)  # e.g., "WhatsApp", "Other"
