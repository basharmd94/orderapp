import traceback  # Added to log the full error stack trace
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Added back
from controllers.user_registration_controller import UserRegistrationController
from controllers.user_login_controller import UserLoginController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from logs import setup_logger
from utils.auth import get_current_user, get_current_admin, SECRET_KEY
from typing import Annotated, List
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user, get_current_admin, oauth2_scheme
from jose import jwt, JWTError  # Import JWT and JWTError for decoding
from sqlalchemy.future import select
from models.users_model import Logged

 

router = APIRouter()
logger = setup_logger()


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def user_registration(
    users: UserRegistrationSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),  # Dependency for async session
):
    logger.info(f"Registration endpoint called: {request.url.path}")
    user_registration_controller = UserRegistrationController(db)  # Pass the session

    try:
        new_user = await user_registration_controller.register_user(users)
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
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ):
    user_login_controller = UserLoginController(db)

    try:
        # Await the call to get_all_users()
        users = await user_login_controller.user_login(form_data)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="""Error! Possible reasons user may be not active, username passord wrong or user already exist in database. Check the full logs""",
        )
    # Return the list of users
    return users
 


@router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),  # Get token from the request
    db: AsyncSession = Depends(get_db)
):
    # Here you can perform actions such as marking the user as logged out.
    # For example, you can remove their session from the database.
    
    # Check if the user is logged in using your token management
    try:
        # Decode the token (this is optional based on your flow)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # Use your actual secret key
        username: str = payload.get("username")
        
        if username is None:
            logger.error(f"User not logged in")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Assuming you have a Logged model that tracks user sessions
    logged_user = await db.execute(select(Logged).filter_by(username=username))  # Make sure to import Logged model
    logged_user = logged_user.scalars().first()

    if not logged_user:
        logger.error(f"User  not logged in")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not logged in"
        )

    # Delete the logged user entry
    await db.delete(logged_user)
    await db.commit()

    logger.info(f"User {username} logged out successfully")

    return {"detail": "User logged out successfully"}