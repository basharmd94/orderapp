import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException, Request
from controllers.db_controllers.test_post_controller import TestPostController
from schemas.test_post_schema import AbdefSchema
from logs import setup_logger
from database import get_db


router = APIRouter()
logger = setup_logger()

@router.post("/create-order-abd", status_code=status.HTTP_201_CREATED)
async def create_order_abd(request: Request, zid: int, order: AbdefSchema, db: AsyncSession = Depends(get_db)):
    logger.info(f"create Test Post Route endpoint called: {request.url.path}")

    # Pass the db session to the TestPostController
    test_post_db_controller = TestPostController(db)
    
    try:
        create_order = await test_post_db_controller.create_order_abdef(zid, order)
        logger.info(f"abdef order created successfully")
        return {"user": create_order}
    except HTTPException as e:
        logger.error(f"Error registering user: {str(e)}")
        raise e 
    except Exception as e:
        logger.error(
            f"Unexpected error during registration: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )