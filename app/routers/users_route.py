import traceback
from fastapi import APIRouter, status, Depends, HTTPException, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from controllers.user_registration_controller import UserRegistrationController
from controllers.user_login_controller import UserLoginController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from logs import setup_logger
from utils.auth import (
    get_current_user, get_current_admin,
    oauth2_scheme
)
from utils.token_utils import (
    create_access_token, blacklist_token,
    is_token_blacklisted, SECRET_KEY, ALGORITHM
)
from typing import Annotated, List
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy.future import select
from models.users_model import Logged, TokenBlacklist, ApiUsers
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()
logger = setup_logger()

@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def user_registration(
    user_data: UserRegistrationSchema,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_registration_controller = UserRegistrationController(db)
        result = await user_registration_controller.register_user(user_data)
        logger.info(f"User {user_data.username} registered successfully from {request.client.host}")
        return result
    except Exception as e:
        logger.error(f"Registration error: {str(e)}\n{traceback.format_exc()}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during user registration"
        )

@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_login_controller = UserLoginController(db)
        result = await user_login_controller.user_login(form_data, request)
        return result
    except Exception as e:
        logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during login"
        )

@router.post("/logout")
async def logout(
    current_user: UserRegistrationSchema = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_login_controller = UserLoginController(db)
        logger.debug(f"Logging out user: {current_user.username}")
        return await user_login_controller.user_logout(token, current_user.username)
    except Exception as e:
        logger.debug(f"Logging out user: {current_user}")
        logger.error(f"Logout error: {str(e)}\n{traceback.format_exc()}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during logout"
        )

@router.post("/refresh-token")
async def refresh_token(
    request: Request,
    refresh_token: str = None,
    db: AsyncSession = Depends(get_db)
    ):
    try:
        # Get refresh token from query params or form data
        refresh_token = request.query_params.get('refresh_token')
        if not refresh_token:
            form_data = await request.form()
            refresh_token = form_data.get('refresh_token')
            
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="refresh_token is required"
            )

        # Check if token is blacklisted
        if await is_token_blacklisted(db, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token format"
            )

        username = payload.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify active session exists
        result = await db.execute(
            select(Logged).filter_by(
                username=username,
                refresh_token=refresh_token,
                status="Logged In"
            )
        )
        logged_user = result.scalar_one_or_none()
        
        if not logged_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No active session found"
            )

        # Generate new access token
        token_data = {
            "username": username,
            "accode": payload.get("accode"),
            "status": payload.get("status"),
            "user_id": payload.get("user_id"),
            "is_admin": payload.get("is_admin"),
            "terminal": payload.get("terminal"),
            "businessId": payload.get("businessId")
        }
        
        new_access_token = await create_access_token(data=token_data)
        
        # Update session
        logged_user.access_token = new_access_token
        logged_user.zutime = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Access token refreshed for user {username} from {request.client.host}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during token refresh"
        )

@router.get("/me", response_model=UserOutSchema)
async def get_current_user_info(
    current_user: UserRegistrationSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current logged in user information"""
    try:
        # Query to get full user details from database
        user_db = UserDBController(db)
        user = await user_db.get_user_by_username(current_user.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return UserOutSchema(
            user_id=user.employeeCode,
            username=user.username,
            email=user.email,
            mobile=user.mobile,
            status=user.status,
            businessId=user.businessId,
            terminal=user.terminal,
            accode=user.accode,
            is_admin=user.is_admin
        )
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not get user information"
        )

@router.get("/sessions", response_model=list)
async def get_user_sessions(
    current_user: UserOutSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all active sessions for the current user"""
    user_login_controller = UserLoginController(db)
    return await user_login_controller.get_user_sessions(current_user.username)

@router.post("/logout/all")
async def logout_all_sessions(
    keep_current: bool = Query(default=False, description="Keep the current session active"),
    current_user: UserOutSchema = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Logout from all sessions"""
    user_login_controller = UserLoginController(db)
    return await user_login_controller.logout_all_sessions(
        current_user.username,
        except_token=token if keep_current else None
    )