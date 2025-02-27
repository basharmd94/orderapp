from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from schemas.customers_schema import (
    CustomersSchema, 
    SalesmanAreaRequest, 
    SalesmanAreaResponse,
    SalesmanAreaUpdateRequest,
    SalesmanUpdateResponse,
    AreaByZidRequest,
    AreaResponse
)
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


@router.post("/get-salesman-area-wise", response_model=SalesmanAreaResponse)
async def get_salesman_by_area(
    request: SalesmanAreaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_admin)  # Changed to admin
):
    """Get salesman information for a specific area in a business. Only accessible by admin users."""
    try:
        customers_controller = CustomersDBController(db)
        result = await customers_controller.get_salesman_by_area(
            zid=request.zid,
            area=request.area
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting salesman info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving salesman information"
        )


@router.post("/update-salesman-area-wise", response_model=SalesmanUpdateResponse)
async def update_salesman_by_area(
    request: SalesmanAreaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_admin)
):
    """Update salesman assignments for customers in a specific area. Only accessible by admin users."""
    try:
        customers_controller = CustomersDBController(db)
        result = await customers_controller.update_salesman_by_area(
            zid=request.zid,
            area=request.area,
            xsp=request.xsp,
            xsp1=request.xsp1,
            xsp2=request.xsp2,
            xsp3=request.xsp3
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating salesman assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating salesman assignments"
        )


@router.post("/get-area-by-zid", response_model=AreaResponse)
async def get_areas_by_zid(
    request: AreaByZidRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user)
):
    """Get all distinct areas for a business ID, optionally filtered by salesman ID."""
    try:
        customers_controller = CustomersDBController(db)
        result = await customers_controller.get_areas_by_zid(
            zid=request.zid,
            user_id=request.user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting areas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving areas"
        )
