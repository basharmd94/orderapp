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
        session = await db.execute(
            select(Logged).filter_by(username=username, access_token=token)
        )
        session = session.scalar()
        
        if session:
            session.zutime = datetime.utcnow()
            await db.commit()
    except Exception as e:
        logger.error(f"Error updating session activity: {str(e)}")
        await db.rollback()

async def session_activity_middleware(request: Request, call_next):
    """Middleware to update session activity timestamp"""
    try:
        # Skip activity update for certain paths
        if request.url.path in [
            "/api/v1/users/login", 
            "/api/v1/users/logout",
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]:
            return await call_next(request)

        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if (auth_header and auth_header.startswith("Bearer ")):
            token = auth_header.split(" ")[1]
            try:
                # Decode token to get username
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("username")
                
                if username:
                    # Get DB session - ensure we have a valid session
                    db = None
                    try:
                        db = request.state.db
                    except AttributeError:
                        db = next(get_db())
                    
                    if db:
                        # Update session activity
                        await update_session_activity(db, username, token)
            except JWTError:
                logger.warning("Invalid token in session activity update")
            except Exception as e:
                logger.error(f"Error updating session activity: {str(e)}")

    except Exception as e:
        logger.error(f"Session middleware error: {str(e)}")

    return await call_next(request)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserOutSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is blacklisted
        if await is_token_blacklisted(db, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception

    database_controller = UserDBController(db)
    
    try:
        user = await database_controller.get_user_by_username(username)
        if user is None:
            raise credentials_exception

        # Check if this specific token has an active session
        logged_query = await db.execute(
            select(Logged).filter(
                Logged.username == username,
                Logged.access_token == token
            )
        )
        logged_user = logged_query.scalar()
        
        if not logged_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No active session found for this token"
            )

        # Log the types for debugging
        logger.debug(f"BusinessId type before conversion: {type(user.businessId)}, value: {user.businessId}")
        
        try:
            # Ensure businessId is an integer
            business_id = int(user.businessId) if user.businessId is not None else None
            logger.debug(f"Converted businessId: {business_id}")

            user_dict = {
                "user_id": user.employeeCode,
                "user_name": user.username,
                "mobile": user.mobile,
                "email": user.email,
                "status": user.status,
                "businessId": business_id,
                "terminal": user.terminal,
                "accode": user.accode,
                "is_admin": user.is_admin,
            }
            logger.debug(f"Final user_dict: {user_dict}")
            return UserOutSchema(**user_dict)
        except ValueError as ve:
            logger.error(f"Error converting businessId: {ve}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid businessId format: {user.businessId}"
            )
        except Exception as conversion_error:
            logger.error(f"Error converting user data: {conversion_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing user data"
            )
            
    except Exception as e:
        logger.error(f"User validation error: {str(e)}\n{traceback.format_exc()}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

async def get_current_user_with_access(
    current_user: UserRegistrationSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    is_admin: bool = False
) -> UserRegistrationSchema:
    try:
        if current_user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active"
            )

        return current_user
    except Exception as e:
        error_msg = f"Access check error for user {current_user.user_name}: {str(e)}"
        logger.error(f"{error_msg}\nStack trace: {traceback.format_exc()}")
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserRegistrationSchema:
    return await get_current_user_with_access(token, db, is_admin=True)

async def get_current_normal_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserRegistrationSchema:
    current_user = await get_current_user(token, db)
    return await get_current_user_with_access(current_user, db, is_admin=False)

