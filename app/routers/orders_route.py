from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from fastapi import APIRouter, status, Depends, HTTPException, Request, Path
from fastapi.responses import JSONResponse
from typing import List

from schemas.orders_schema import OpmobSchema, BulkOpmobSchema, OpmobResponse
from schemas.user_schema import UserRegistrationSchema
from logs import setup_logger
from utils.auth import get_current_normal_user
from controllers.db_controllers.orders_db_controller import OrderDBController
import traceback

router = APIRouter(
    tags=["Orders"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)

logger = setup_logger()

async def handle_order_creation(
    request: Request,
    zid: int,
    order: OpmobSchema,
    current_user: UserRegistrationSchema,
    db: AsyncSession
) -> List[OpmobResponse]:
    """
    Helper function to handle order creation logic
    """
    order_db_controller = OrderDBController(db)
    try:
        created_items = await order_db_controller.create_order(zid, order, current_user)
        logger.info(f"Order created by {current_user.user_name}, id {current_user.user_id}")
        return created_items
    except ValueError as e:
        logger.error(f"Validation error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "type": "validation_error"}
        )
    except Exception as e:
        logger.error(f"Unexpected error creating order: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "type": "server_error"}
        )

@router.post(
    "/create-order",
    status_code=status.HTTP_201_CREATED,
    response_model=List[OpmobResponse],
    summary="Create a new order",
    description="Creates a new order with the given items for a specific customer"
)
async def create_order(
    request: Request,
    order: OpmobSchema,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new order with the following information:
    - Business ID (zid)
    - Customer details (ID, name, address)
    - List of items with quantities and prices
    - Location information (optional)
    
    Example request body:
    {
        "zid": 100,
        "xcus": "CUS-000001",
        "xcusname": "Customer Name",
        "xcusadd": "Customer Address",
        "items": [...]
    }
    
    Returns:
        List of created order items
    """
    return await handle_order_creation(request, order.zid, order, current_user, db)

@router.post(
    "/create-bulk-order",
    status_code=status.HTTP_201_CREATED,
    response_model=List[OpmobResponse],
    summary="Create multiple orders in bulk",
    description="Creates multiple orders at once for different customers"
)
async def create_bulk_order(
    request: Request,
    orders_data: BulkOpmobSchema,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple orders in bulk with the following information for each order:
    - Business ID (zid)
    - Customer details (ID, name, address)
    - List of items with quantities and prices
    - Location information (optional)
    
    Example request body:
    {
        "orders": [
            {
                "zid": 100,
                "xcus": "CUS-000001",
                "xcusname": "Customer Name",
                "xcusadd": "Customer Address",
                "items": [...]
            },
            {
                "zid": 100,
                "xcus": "CUS-000002",
                "xcusname": "Customer Name 2",
                "xcusadd": "Customer Address 2",
                "items": [...]
            }
        ]
    }
    
    Returns:
        List of all created order items
    """
    logger.info(f"Create bulk order endpoint called by: {request.url.path}")
    order_db_controller = OrderDBController(db)

    try:
        created_items = []
        for order in orders_data.orders:
            items = await handle_order_creation(request, order.zid, order, current_user, db)
            created_items.extend(items)
        
        logger.info(f"Bulk orders created by {current_user.user_name}, id {current_user.user_id}")
        return created_items
        
    except HTTPException as e:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating bulk orders: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Error creating bulk orders", "type": "server_error"}
        )

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check if the orders service is running"
)
async def health_check():
    """
    Simple health check endpoint to verify the service is running
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "service": "orders"}
    )
