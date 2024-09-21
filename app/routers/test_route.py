import traceback  # Added to log the full error stack trace
from fastapi import APIRouter, status, Depends, HTTPException, Request
from controllers.user_registration_controller import UserRegistrationController
from controllers.user_login_controller import UserLoginController
from controllers.db_controllers.test_db_controller import TestDbController
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from logs import setup_logger
from utils.auth import get_current_user, get_current_admin
from typing import Annotated, List

router = APIRouter()
logger = setup_logger()





@router.get("/testroute", response_model=List[UserOutSchema], status_code=status.HTTP_200_OK)
async def getallusers(
    request: Request,
    limit: int = 10,
    offset: int = 0,
):
    logger.info(f"get all users endpoint called: {request.url.path}")

    test_db_controller = TestDbController()

    # Ensure to connect before calling any methods
    await test_db_controller.connect()

    try:
        # Await the call to get_all_users()
        users = await test_db_controller.get_all_users()
    finally:
        # Close the session regardless of success or failure
        await test_db_controller.close()

    # Return the list of users
    return users
 