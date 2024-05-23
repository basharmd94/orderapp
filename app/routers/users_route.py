from fastapi import APIRouter, status, Depends, HTTPException, Request
from controllers.user_registration_controller import UserRegistrationController
from controllers.user_login_controller import UserLoginController
from schemas.user_schema import UserRegistrationSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from logs import setup_logger
from utils.auth import get_current_user, get_current_admin, get_current_normal_user
from typing import Annotated

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


@router.post("/login")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_login_controller = UserLoginController()

    try:
        tokens = await user_login_controller.user_login(form_data)
        return tokens
    except HTTPException as e:
        raise e


#  DEMO
# @router.get("/protected/endpoint")
# async def protected_endpoint(request : Request, current_user: UserRegistrationSchema = Depends(get_current_user)):
#     print (request.url.path)
#     if current_user.status != "active":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
#     return {"message": "This is a protected endpoint"}


# @router.get("/me")
# async def hello(request:Request, current_user: UserRegistrationSchema = Depends(get_current_user)):
#     print (request.url.path)
#     return "hello"


# @router.get("/protected/admin-endpoint")
# async def protected_admin_endpoint(request: Request, current_user: UserRegistrationSchema = Depends(get_current_admin)):
#     return {"message": "This is a protected admin endpoint"}

# @router.get("/protected/user-endpoint")
# async def protected_user_endpoint(request: Request, current_user: UserRegistrationSchema = Depends(get_current_normal_user)):
#     return {"message": "This is a protected user endpoint"}
