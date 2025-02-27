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


@router.put(
    "/update-customer-by-area/{zid}",
    response_model=List[CustomersSchema],
    summary="Update Customers via area",
    description="Update all customers based on filter criteria.",
    responses={418: {"description": "Customers route"}},
)
async def get_all_customers(
    request: Request,
    zid: int,
    area_name: Annotated[
        str,
        Query(
            min_length=3,
            description="Put Customers ID",
        ),
    ],
    xsp: Annotated[Union[str, None], Query(min_length=3)] = None,
    xsp1: Annotated[Union[str, None], Query(min_length=3)] = None,
    xsp2: Annotated[Union[str, None], Query(min_length=3)] = None,
    xsp3: Annotated[Union[str, None], Query(min_length=3)] = None,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    db: AsyncSession = Depends(get_db),
):

    customers_db_controller = CustomersDBController(db)

    try:
        customers = await customers_db_controller.get_all_customers(
            zid, customer, limit, offset
        )
        if not customers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_details("No customers found"),
            )
        # print ("customers_route /", current_user)
        return customers

    except ValueError as e:
        logger.error(f"Error getting Customer route: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating order: {e}")
        raise HTTPException(status_code=500, detail="Error creating order")
        print(traceback.format_exc())


@router.get(
    "/all-sync",
    response_model=List[CustomersSchema],
    summary="Get all customers across all businesses",
    description="Get all customers from all businesses for a specific employee ID"
)
async def get_all_customers_sync(
    request: Request,
    employee_id: Annotated[
        str,
        Query(
            min_length=3,
            description="Put Employee ID, like SA--000015",
        ),
    ],
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    customers_db_controller = CustomersDBController(db)

    try:
        customers = await customers_db_controller.get_all_customers_sync(
            employee_id, limit, offset, current_user
        )
        if not customers:
            logger.info(f"No customers found for employee ID: {employee_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No customers found for employee ID: {employee_id}"
            )
        return customers

    except ValueError as e:
        logger.error(f"Error getting Customer route sync: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        # Re-raise HTTP exceptions to preserve status code
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_all_customers_sync: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving customers"
        )
