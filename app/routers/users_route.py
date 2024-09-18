import traceback  # Added to log the full error stack trace
from fastapi import APIRouter, status, Depends, HTTPException, Request
from controllers.user_registration_controller import UserRegistrationController
from controllers.user_login_controller import UserLoginController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from logs import setup_logger
from utils.auth import get_current_user, get_current_admin
from typing import Annotated, List

router = APIRouter()
logger = setup_logger()


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def user_registration(users: UserRegistrationSchema, request: Request):
    logger.info(f"Registration endpoint called: {request.url.path}")
    user_registration_controller = UserRegistrationController()

    try:
        new_user = user_registration_controller.register_user(users)
        logger.info(f"User registered successfully: {new_user.username}")
        return {"user": new_user}
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




@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_login_controller = UserLoginController()
    return await user_login_controller.user_login(form_data)







@router.get("/getallusers", response_model= List[UserOutSchema] , status_code=status.HTTP_200_OK)
async def getallusers(
    request:Request,
    limit: int = 10,
    offset: int = 0,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    
    ):
    logger.info(f"get all users endpoint called: {request.url.path}")
    user_db_controller = UserDBController()
    users = user_db_controller.get_all_users()
    # Return the list of users
    return users
