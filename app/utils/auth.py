# auth.py
import traceback
from fastapi import HTTPException, Depends, status, Request
from datetime import datetime
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from models.users_model import ApiUsers, Logged
from controllers.db_controllers.user_db_controller import UserDBController
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from logs import setup_logger
from sqlalchemy.future import select
from utils.token_utils import (
    SECRET_KEY, ALGORITHM, is_token_blacklisted
)

logger = setup_logger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

async def update_session_activity(db: AsyncSession, username: str, token: str):
    """Update the last activity time for a session"""
    try:
        result = await db.execute(
            select(Logged).filter_by(username=username, access_token=token)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.zutime = datetime.utcnow()
            await db.commit()
        else:
            logger.warning(f"No active session found for user {username}")
            
    except Exception as e:
        logger.error(f"Error updating session activity: {str(e)}")
        await db.rollback()
async def session_activity_middleware(request: Request, call_next):
    """Middleware to update session activity timestamp"""
    response = None

    try:
        # Skip session activity updates for specific paths
        if request.url.path in [
            "/api/v1/users/login",
            "/api/v1/users/logout",
            "/api/v1/users/refresh-token",
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]:
            return await call_next(request)

        # Extract the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decode the JWT token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("username")

                if username:
                    # Resolve the database session from get_db()
                    async for db in get_db():
                        # Update session activity
                        await update_session_activity(db, username, token)
                        break  # Exit after using the session

            except JWTError:
                logger.warning("Invalid token in session activity update")
            except Exception as e:
                logger.error(f"Error updating session activity: {str(e)}")
    except Exception as e:
        logger.error(f"Session middleware error: {str(e)}")

    # Call the next middleware or route handler
    if response is None:
        response = await call_next(request)

    return response

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserOutSchema:
    """Retrieve the currently authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        if await is_token_blacklisted(db, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception

        database_controller = UserDBController(db)
        user = await database_controller.get_user_by_username(username)
        if not user:
            raise credentials_exception

        if user.status.lower() != "active":  # Ensure user status is "active"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )

        logged_query = await db.execute(
            select(Logged).filter(Logged.username == username, Logged.access_token == token)
        )
        logged_user = logged_query.scalar()
        
        if not logged_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No active session found for this token"
            )
        
        return user
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"User validation error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

async def get_current_admin(current_user: UserOutSchema = Depends(get_current_user)) -> UserOutSchema:
    """Dependency to ensure the current user is an admin."""
    if current_user.is_admin.lower() != "admin":  # Check admin role
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized as an admin"
        )
    return current_user

async def get_current_normal_user(current_user: UserOutSchema = Depends(get_current_user)) -> UserOutSchema:
    """Dependency to ensure normal users can access, but allow admins too."""
    return current_user  # Admins can access all routes, normal users are restricted where needed