from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from schemas.customers_schema import CustomersSchema
from schemas.user_schema import UserRegistrationSchema
from typing import List
from typing_extensions import Annotated
from utils.auth import get_current_normal_user
from utils.error import error_details
from controllers.db_controllers.customers_db_controller import (
    CustomersDBController,
)  # Import the controller
from logs import setup_logger

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
    limit: int = 10,
    offset: int = 0,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):

    customers = CustomersDBController.get_all_customers(zid, customer, limit, offset)
    if not customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No customers found"),
        )
    # print ("customers_route /", current_user)
    return customers
