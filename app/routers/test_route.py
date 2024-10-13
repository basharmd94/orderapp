from fastapi import APIRouter, status, Depends, HTTPException, Request
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from logs import setup_logger
from utils.auth import get_current_normal_user
from controllers.db_controllers.orders_db_controller import OrderDBController
import traceback


router = APIRouter()
logger = setup_logger()



 
@router.post("/create-abdef-one/{zid}", status_code=status.HTTP_201_CREATED)
async def create_order(
    request: Request,
    zid: int,
    order: OpmobSchema,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    logger.info(f"Create order endpoint called by: {request.url.path}")

    order_db_controller = OrderDBController()
    await order_db_controller.connect()

    try: 
        
        created_items = await order_db_controller.create_order(zid, order, current_user)
        
    except ValueError as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}")
        raise HTTPException(status_code=500, detail="Error creating order")
        print(traceback.format_exc())

    finally:
        await order_db_controller.close()
    return created_items
 