from fastapi import APIRouter, HTTPException, status, Query, Depends, Request, Path, Response
from schemas.manufacturing_schema import (
    ManufacturingOrderSchema,
    ManufacturingOrderListResponse,
    ManufacturingOrderDetailSchema
)
from typing import List, Optional
# from typing_extensions import Annotated
from utils.auth import get_current_admin
from utils.error import error_details
from controllers.db_controllers.manufacturing_db_controller import (
    ManufacturingDBController,
)
from logs import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import math
import csv
import io

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

@router.get(
    "/mo-details/{zid}/{mo_number}",
    response_model=List[ManufacturingOrderDetailSchema],
    summary="Get Manufacturing Order Details",
    description="Retrieve detailed information for a specific manufacturing order"
)
async def get_mo_detail(
    request: Request,
    zid: int = Path(..., description="Company ID", ge=1),
    mo_number: str = Path(..., description="Manufacturing Order Number"),
    current_user: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific manufacturing order.
    
    - **zid**: Company ID (required)
    - **mo_number**: Manufacturing Order Number (required)
    
    Returns a list of items used in the manufacturing order with quantities, rates, and costs.
    """
    try:
        # Initialize manufacturing DB controller
        manufacturing_controller = ManufacturingDBController(db)
        
        # Get manufacturing order details
        mo_details = await manufacturing_controller.get_mo_detail(
            zid=zid,
            mo_number=mo_number
        )
        
        # Return the raw list (no need to wrap in an object with "items" field)
        return mo_details
        
    except HTTPException as he:
        # Re-raise HTTP exceptions without modifying them
        raise he
    except Exception as e:
        logger.error(f"Error in get_mo_detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details(f"Failed to retrieve manufacturing order details: {str(e)}")
        )

@router.get(
    "/mo-export/{zid}/{mo_number}",
    summary="Export Manufacturing Order Details as CSV",
    description="Export detailed information for a specific manufacturing order as a CSV file. Note: Use direct API URL in browser to download, not through Swagger UI.",
    response_class=Response
)
async def export_mo_detail_csv(
    request: Request,
    zid: int = Path(..., description="Company ID", ge=1),
    mo_number: str = Path(..., description="Manufacturing Order Number"),
    download: bool = Query(True, description="Set to false to view in browser without downloading"),
    current_user: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Export detailed information about a specific manufacturing order as a CSV file.
    
    - **zid**: Company ID (required)
    - **mo_number**: Manufacturing Order Number (required)
    - **download**: Set to false to view in browser without downloading (default: true)
    
    Returns a CSV file containing details of items used in the manufacturing order.
    
    **Note:** For file download, access the URL directly in browser, not through Swagger UI:
    `/mo-export/{zid}/{mo_number}`
    """
    try:
        # Initialize manufacturing DB controller
        manufacturing_controller = ManufacturingDBController(db)
        
        # Get manufacturing order details using the existing controller method
        mo_details = await manufacturing_controller.get_mo_detail(
            zid=zid,
            mo_number=mo_number
        )
        
        # Create a CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            "Item Code", 
            "Description", 
            "Unit", 
            "Quantity", 
            "Rate", 
            "Total Amount", 
            "Cost Per Item", 
            "Available Stock"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for item in mo_details:
            writer.writerow([
                item["xitem"],
                item["xdesc"],
                item["xunit"],
                item["raw_qty"],
                item["rate"],
                item["total_amt"],
                item["cost_per_item"],
                item["stock"]
            ])
        
        # Prepare the CSV file for response
        output.seek(0)
        csv_content = output.getvalue()
        
        # Create response with appropriate headers for file download
        filename = f"MO_{mo_number}_details.csv"
        response = Response(
            content=csv_content,
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
        
    except HTTPException as he:
        # Re-raise HTTP exceptions without modifying them
        raise he
    except Exception as e:
        logger.error(f"Error in export_mo_detail_csv: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_details(f"Failed to export manufacturing order details: {str(e)}")
        )
