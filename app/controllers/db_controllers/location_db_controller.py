from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from models.users_model import ApiUsers
from location import LocationRecord, LocationCreate, Location, LocationQuery
import asyncio
from asyncio import Queue
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
from logs import setup_logger

logger = setup_logger()

class LocationDBController:
    """Controller for handling location-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db  # Use the session passed in from the route handler

    async def create_location(self, location_data: LocationCreate) -> LocationRecord:
        """
        Create a new location record in the database.
        
        Args:
            location_data: The location data to create
            
        Returns:
            The created location record
        """
        if self.db is None:
            raise Exception("Database session not initialized.")
            
        # Create a new LocationRecord object
        new_location = LocationRecord(
            username=location_data.username,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            altitude=location_data.altitude,
            accuracy=location_data.accuracy,
            name=location_data.name,
            street=location_data.street,
            district=location_data.district,
            city=location_data.city,
            region=location_data.region,
            postal_code=location_data.postal_code,
            country=location_data.country,
            formatted_address=location_data.formatted_address,
            maps_url=location_data.maps_url,
            timestamp=location_data.timestamp,
            business_id=location_data.business_id,
            notes=location_data.notes,
            device_info=location_data.device_info,
            is_check_in=location_data.is_check_in,
            shared_via=location_data.shared_via
        )
        
        # Add to session and commit
        self.db.add(new_location)
        await self.db.commit()
        await self.db.refresh(new_location)
        
        return new_location
        
    async def get_locations(self, query_params: LocationQuery) -> List[LocationRecord]:
        """
        Retrieve location records based on query parameters.
        
        Args:
            query_params: Parameters to filter locations by
            
        Returns:
            A list of location records matching the criteria
        """
        if self.db is None:
            raise Exception("Database session not initialized.")
            
        # Build base query
        query = select(LocationRecord)
        
        # Apply filters if provided
        if query_params.username:
            query = query.filter(LocationRecord.username == query_params.username)
            
        if query_params.business_id:
            query = query.filter(LocationRecord.business_id == query_params.business_id)
            
        if query_params.start_date:
            query = query.filter(LocationRecord.timestamp >= query_params.start_date)
            
        if query_params.end_date:
            query = query.filter(LocationRecord.timestamp <= query_params.end_date)
            
        # Apply sorting, limit and offset
        query = query.order_by(LocationRecord.timestamp.desc())
        
        if query_params.limit:
            query = query.limit(query_params.limit)
            
        if query_params.offset:
            query = query.offset(query_params.offset)
            
        # Execute query
        result = await self.db.execute(query)
        locations = result.scalars().all()
        
        return locations
    
    async def get_last_location(self, username: str) -> Optional[LocationRecord]:
        """
        Get the most recent location for a specific user.
        
        Args:
            username: The username to get the last location for
            
        Returns:
            The most recent location record or None if not found
        """
        if self.db is None:
            raise Exception("Database session not initialized.")
            
        query = (
            select(LocationRecord)
            .filter(LocationRecord.username == username)
            .order_by(LocationRecord.timestamp.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        location = result.scalars().first()
        
        return location
