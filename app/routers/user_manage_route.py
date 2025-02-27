from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from schemas.customers_schema import CustomersSchema
from schemas.user_schema import UserRegistrationSchema
from typing import List, Union
from typing_extensions import Annotated
from utils.auth import get_current_normal_user, get_current_admin
from utils.error import error_details
from controllers.db_controllers.customers_db_controller import (
    CustomersDBController,
)
from logs import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()
logger = setup_logger()


@router.get("/all/{zid}", response_model=List[CustomersSchema])
async def get_all_customers(
    request: Request,
    zid: int,
    customer: Annotated[
        str,
        Query(
            min_length=3,
            description="Put Customers ID, Customers Name or Area like CUS-001202 ",
        ),
    ],
    employee_id : Annotated[ 
        str,
        Query(
            min_length=3,
            description="Put Employee ID, like SA--000015 ",
        ),
    ] ,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    customers_db_controller = CustomersDBController(db)

    try:
        customers = await customers_db_controller.get_all_customers(
            zid, customer, employee_id, limit, offset, current_user
        )
        return customers

    except ValueError as e:
        logger.error(f"Error getting Customer route: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        # Re-raise HTTP exceptions to preserve status code
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_all_customers: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving customers"
        )
