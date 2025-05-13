from fastapi import APIRouter, HTTPException, status, Query, Depends, Request, Path
from schemas.manufacturing_schema import (
    ManufacturingOrderSchema,
    ManufacturingOrderListResponse
)
from typing import List, Union, Optional
from typing_extensions import Annotated
from utils.auth import get_current_admin
from utils.error import error_details
from controllers.db_controllers.manufacturing_db_controller import (
    ManufacturingDBController,
)
from logs import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import math

router = APIRouter()
logger = setup_logger()

@router.get(
    "/mo/{zid}",
    response_model=ManufacturingOrderListResponse,
    summary="Get Manufacturing Orders",
    description="Retrieve manufacturing orders with optional filtering and pagination"
)
async def get_all_mo(
    request: Request,
    zid: int = Path(..., description="Company ID", ge=1),
    search_text: Optional[str] = Query(None, description="Search by item code, item name, date or MO number"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Items per page", ge=1, le=100),
    current_user: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all manufacturing orders with filtering and pagination.
    
    - **zid**: Company ID (required)
    - **search_text**: Optional text to search in item code, item name, date, or MO number
    - **page**: Page number (1-based, default: 1)
    - **size**: Number of items per page (default: 10)
    
    Returns a paginated list of manufacturing orders.
    """
    try:
        # Initialize manufacturing DB controller
        manufacturing_controller = ManufacturingDBController(db)
        
        # Get manufacturing orders with pagination
        mo_data, total_count = await manufacturing_controller.get_all_mo(
            zid=zid,
            search_text=search_text,
            page=page,
            size=size
        )
        
        # Calculate pagination details
        total_pages = math.ceil(total_count / size) if total_count > 0 else 0
        
        # Create the response
        response = ManufacturingOrderListResponse(
            items=mo_data,
            total=total_count,
            page=page,
            size=size,
            pages=total_pages
        )
        
        return response
        
    except Exception as e:
        # logger.error(f"Error in get_all_mo: {str(e)}")
        logger.error("Error in get_all_mo: ")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details("Failed to retrieve manufacturing orders: from route ")
        )
