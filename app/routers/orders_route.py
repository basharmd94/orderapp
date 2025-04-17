from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, async_session_maker
from fastapi import APIRouter, status, Depends, HTTPException, Request, Path, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
from asyncio import Queue

from schemas.orders_schema import OpmobSchema, BulkOpmobSchema, OpmobResponse
from schemas.order_summary_schema import OrderSummaryListResponse
from schemas.user_schema import UserRegistrationSchema
from logs import setup_logger
from utils.auth import get_current_normal_user
from utils.permissions import has_permission
from controllers.db_controllers.orders_db_controller import OrderDBController
import traceback
from datetime import datetime

router = APIRouter(
    tags=["Orders"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)

logger = setup_logger()

# Configure the maximum number of concurrent operations
MAX_CONCURRENT_OPERATIONS = 5

# Helper to convert Opmob object to OpmobResponse
def convert_to_opmob_response(item) -> OpmobResponse:
    """Convert database model to Pydantic schema for response"""
    # Create a dictionary with all attributes that exist in the database model
    item_dict = {
        "invoicesl": item.invoicesl,
        "xroword": item.xroword,
        "zutime": item.zutime or datetime.now(),
        "xdate": item.xdate or datetime.now(),
        "xqty": item.xqty,
        "xlat": item.xlat,
        "xlong": item.xlong,
        "xlinetotal": float(item.xlinetotal) if item.xlinetotal is not None else 0.0,
        "xtra1": item.xtra1 if hasattr(item, 'xtra1') else None,
        "xtra2": item.xtra2 if hasattr(item, 'xtra2') else None,
        "xprice": float(item.xprice) if item.xprice is not None else 0.0,
        "ztime": item.ztime or datetime.now(),
        "zid": item.zid,
        "xtra3": item.xtra3 if hasattr(item, 'xtra3') else None,
        "xtra4": item.xtra4 if hasattr(item, 'xtra4') else None,
        "xtra5": item.xtra5 if hasattr(item, 'xtra5') else None,
        "invoiceno": item.invoiceno,
        "username": item.username,
        "xemp": item.xemp,
        "xcus": item.xcus,
        "xcusname": item.xcusname,
        "xcusadd": item.xcusadd,
        "xitem": item.xitem,
        "xdesc": item.xdesc,
        "xstatusord": item.xstatusord if hasattr(item, 'xstatusord') else None,
        "xordernum": item.xordernum if hasattr(item, 'xordernum') else None,
        "xterminal": item.xterminal,
        "xsl": item.xsl,
    }
    return OpmobResponse(**item_dict)

async def process_single_order(order: OpmobSchema, current_user: UserRegistrationSchema) -> List[OpmobResponse]:
    """Process a single order with its own database session"""
    session = async_session_maker()
    try:
        logger.info(f"Creating new database session for order processing customer: {order.xcus}")
        order_db_controller = OrderDBController(session)
        
        # Removed the session.begin() context manager as the controller handles its own transactions
        logger.info(f"Starting order creation for customer {order.xcus} with {len(order.items)} items")
        created_items = await order_db_controller.create_order(order.zid, order, current_user)
        logger.info(f"Order created successfully for customer {order.xcus} with {len(created_items)} items")
        
        # Convert DB models to Pydantic models
        response_items = [convert_to_opmob_response(item) for item in created_items]
        logger.info(f"Converted {len(response_items)} DB items to response models")
        return response_items
    except Exception as e:
        logger.error(f"Error processing order for customer {order.xcus}: {str(e)}\n{traceback.format_exc()}")
        raise
    finally:
        await session.close()
        logger.info(f"Closed database session for customer {order.xcus}")

async def process_order_queue(queue: Queue, current_user: UserRegistrationSchema) -> List[OpmobResponse]:
    """Process orders from the queue concurrently"""
    created_items = []
    orders_processed = 0
    while True:
        try:
            order = await queue.get()
            if order is None:  # Sentinel value to indicate end of queue
                logger.info("Worker received sentinel value, ending processing")
                break
            
            orders_processed += 1
            logger.info(f"Processing order #{orders_processed} for customer {order.xcus} with {len(order.items)} items")
                
            items = await process_single_order(order, current_user)
            if items:
                created_items.extend(items)
                logger.info(f"Added {len(items)} items to result, total: {len(created_items)}")
            else:
                logger.warning(f"Order processing returned no items for customer {order.xcus}")
        except Exception as e:
            logger.error(f"Error processing order: {str(e)}\n{traceback.format_exc()}")
            # Continue processing other orders
        finally:
            queue.task_done()
    
    # Log the results for debugging
    logger.info(f"Worker finished with {len(created_items)} items")
    return created_items

async def handle_order_creation(
    request: Request,
    zid: int,
    order: OpmobSchema,
    current_user: UserRegistrationSchema,
    db: AsyncSession
) -> List[OpmobResponse]:
    """Helper function to handle order creation logic"""
    try:
        order_db_controller = OrderDBController(db)
        db_items = await order_db_controller.create_order(zid, order, current_user)
        logger.info(f"Order created by {current_user.username}, id {current_user.user_id}")
        
        # Convert DB models to Pydantic models
        return [convert_to_opmob_response(item) for item in db_items]
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
@has_permission("order.create")  # Apply permission check
async def create_order(
    request: Request,
    order: OpmobSchema,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    return await handle_order_creation(request, order.zid, order, current_user, db)

@router.post(
    "/create-bulk-order",
    status_code=status.HTTP_201_CREATED,
    response_model=List[OpmobResponse],
    summary="Create multiple orders in bulk",
    description="Creates multiple orders at once for different customers using concurrent processing"
)
# @has_permission("order.bulk_create")  # Apply permission check for bulk operations
async def create_bulk_order(
    request: Request,
    orders_data: BulkOpmobSchema,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple orders concurrently using an asyncio Queue to manage concurrency.
    """
    logger.info(f"Create bulk order endpoint called by: {request.url.path} with {len(orders_data.orders)} orders")
    
    if not orders_data.orders:
        logger.warning("No orders provided in request")
        return []
    
    try:
        # Log request details
        logger.info(f"Processing bulk order request with {len(orders_data.orders)} orders")
        logger.info(f"First order data: Customer: {orders_data.orders[0].xcus}, Items: {len(orders_data.orders[0].items)}")
        
        # For non-concurrent processing (fallback)
        if len(orders_data.orders) == 1:
            logger.info("Processing single order directly")
            order_controller = OrderDBController(db)
            db_items = await order_controller.create_order(
                orders_data.orders[0].zid, 
                orders_data.orders[0], 
                current_user
            )
            logger.info(f"Single order processed, created {len(db_items)} items")
            # Convert DB models to Pydantic response models
            response_items = [convert_to_opmob_response(item) for item in db_items]
            logger.info(f"Returning {len(response_items)} response items")
            return response_items
        
        # Create a queue and populate it with orders
        order_queue = Queue()
        for order in orders_data.orders:
            await order_queue.put(order)
            
        # Add sentinel values to signal end of queue
        worker_count = min(MAX_CONCURRENT_OPERATIONS, len(orders_data.orders))
        for _ in range(worker_count):
            await order_queue.put(None)
        
        logger.info(f"Starting {worker_count} worker tasks")
        
        # Process orders concurrently
        tasks = []
        for i in range(worker_count):
            task = asyncio.create_task(process_order_queue(order_queue, current_user))
            tasks.append(task)
        
        # Wait for all tasks to complete
        all_results = await asyncio.gather(*tasks)
        logger.info(f"All tasks completed, merging results from {len(all_results)} workers")
        
        # Merge results from all workers
        final_results = []
        for result_list in all_results:
            if isinstance(result_list, list):
                final_results.extend(result_list)
                logger.info(f"Added {len(result_list)} items from a worker")
            else:
                logger.warning(f"Worker returned non-list result: {type(result_list)}")
        
        logger.info(f"Final result has {len(final_results)} items")
        
        # Our results are already Pydantic models at this point
        return final_results
        
    except Exception as e:
        logger.error(f"Unexpected error creating bulk orders: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"Error creating bulk orders: {str(e)}", "type": "server_error"}
        )

@router.get(
    "/get-pending-orders",
    status_code=status.HTTP_200_OK,
    response_model=OrderSummaryListResponse,
    summary="Get pending orders",
    description="Retrieve the last 10 pending (new) orders for the current user"
)
async def get_pending_orders(
    request: Request,
    zid: Optional[int] = Query(None, description="Optional business ID filter"),
    limit: int = Query(10, description="Maximum number of orders to return", ge=1, le=100),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the last 10 pending (new) orders for the current user."""
    try:
        order_controller = OrderDBController(db)
        result = await order_controller.get_pending_orders(
            username=current_user.username,
            zid=zid,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error retrieving pending orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pending orders: {str(e)}"
        )

@router.get(
    "/get-confirmed-orders",
    status_code=status.HTTP_200_OK,
    response_model=OrderSummaryListResponse,
    summary="Get confirmed orders",
    description="Retrieve the last 10 confirmed orders for the current user"
)
async def get_confirmed_orders(
    request: Request,
    zid: Optional[int] = Query(None, description="Optional business ID filter"),
    limit: int = Query(10, description="Maximum number of orders to return", ge=1, le=100),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the last 10 confirmed orders for the current user."""
    try:
        order_controller = OrderDBController(db)
        result = await order_controller.get_confirmed_orders(
            username=current_user.username,
            zid=zid,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error retrieving confirmed orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving confirmed orders: {str(e)}"
        )

@router.get(
    "/get-cancelled-orders",
    status_code=status.HTTP_200_OK,
    response_model=OrderSummaryListResponse,
    summary="Get cancelled orders",
    description="Retrieve the last 10 cancelled orders for the current user"
)
async def get_cancelled_orders(
    request: Request,
    zid: Optional[int] = Query(None, description="Optional business ID filter"),
    limit: int = Query(10, description="Maximum number of orders to return", ge=1, le=100),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the last 10 cancelled orders for the current user."""
    try:
        order_controller = OrderDBController(db)
        result = await order_controller.get_cancelled_orders(
            username=current_user.username,
            zid=zid,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error retrieving cancelled orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cancelled orders: {str(e)}"
        )

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Check if the orders service is running"
)
async def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy", "service": "orders"}
    )
