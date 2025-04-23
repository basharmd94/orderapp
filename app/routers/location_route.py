from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, async_session_maker
from controllers.db_controllers.location_db_controller import LocationDBController
from location import LocationCreate, Location, LocationQuery
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_normal_user
from utils.error import error_details
from logs import setup_logger
from typing import List, Optional
import asyncio
from asyncio import Queue
import traceback
from datetime import datetime

router = APIRouter(
    tags=["Location"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)

logger = setup_logger()

# Configure the maximum number of concurrent operations
MAX_CONCURRENT_OPERATIONS = 5

# Helper to convert LocationRecord to Location (response model)
def convert_to_location_response(record) -> Location:
    """Convert database model to Pydantic schema for response"""
    return Location(
        id=record.id,
        username=record.username,
        latitude=record.latitude,
        longitude=record.longitude,
        altitude=record.altitude,
        accuracy=record.accuracy,
        name=record.name,
        street=record.street,
        district=record.district,
        city=record.city,
        region=record.region,
        postal_code=record.postal_code,
        country=record.country,
        formatted_address=record.formatted_address,
        maps_url=record.maps_url,
        timestamp=record.timestamp,
        created_at=record.created_at,
        business_id=record.business_id,
        notes=record.notes,
        device_info=record.device_info,
        is_check_in=record.is_check_in,
        shared_via=record.shared_via
    )

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=Location,
    summary="Create a new location record",
    description="Create a new location record for tracking user location"
)
async def create_location(
    request: Request,
    location_data: LocationCreate,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new location record for a user."""
    try:
        logger.info(f"Create location endpoint called: {request.url.path} by user: {current_user.username} (ID: {current_user.id})")
        
        # Ensure the user can only create locations for themselves unless they're an admin
        if location_data.username != current_user.username and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_details("You can only create location records for yourself")
            )
        location_db_controller = LocationDBController(db)
        location_record = await location_db_controller.create_location(location_data)
        
        return convert_to_location_response(location_record)
    except Exception as e:
        logger.error(f"Error creating location record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details(f"Error creating location record: {str(e)}")
        )

@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=List[Location],
    summary="Query location records",
    description="Search for location records using various filters"
)
async def get_locations(
    request: Request,
    query_params: LocationQuery,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Query location records based on various filters."""
    try:
        logger.info(f"Query locations endpoint called: {request.url.path} by user: {current_user.username} (ID: {current_user.id})")
        
        # Non-admin users can only query their own locations
        if not current_user.is_admin and query_params.username and query_params.username != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_details("You can only query your own location records")
            )
        
        # If no username provided and not admin, default to current user
        if not query_params.username and not current_user.is_admin:
            query_params.username = current_user.username
        
        location_db_controller = LocationDBController(db)
        locations = await location_db_controller.get_locations(query_params)
        
        if not locations:
            logger.info("No location records found matching query")
            return []
        
        logger.info(f"Found {len(locations)} location records")
        return [convert_to_location_response(location) for location in locations]
    except Exception as e:
        logger.error(f"Error querying location records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details(f"Error querying location records: {str(e)}")
        )

@router.get(
    "/last/{username}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[Location],
    summary="Get last location for user",
    description="Get the most recent location record for a specific user"
)
async def get_last_location(
    request: Request,
    username: str,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent location for a specific user."""
    try:
        logger.info(f"Get last location endpoint called: {request.url.path} by user: {current_user.username} (ID: {current_user.id})")
        
        # Non-admin users can only get their own last location
        if username != current_user.username and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_details("You can only view your own location records")
            )
        
        location_db_controller = LocationDBController(db)
        location = await location_db_controller.get_last_location(username)
        
        if not location:
            logger.info(f"No location record found for user {username}")
            return None
        
        return convert_to_location_response(location)
    except Exception as e:
        logger.error(f"Error getting last location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details(f"Error getting last location: {str(e)}")
        )
