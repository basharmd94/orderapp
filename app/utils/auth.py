# auth.py
import traceback
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from schemas.user_schema import UserRegistrationSchema, UserOutSchema
from models.users_model import ApiUsers, Logged, TokenBlacklist
from controllers.db_controllers.user_db_controller import UserDBController
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from logs import setup_logger
from dotenv import load_dotenv
import os
from sqlalchemy.future import select
from sqlalchemy import delete, and_

# Load environment variables
load_dotenv()

# Check if required environment variables are set
if not os.getenv("SECRET_KEY"):
    raise ValueError("SECRET_KEY environment variable is not set")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

logger = setup_logger()

# Log warning if any of these values are missing
if not ALGORITHM:
    logger.error("ALGORITHM environment variable is not set")
    raise ValueError("ALGORITHM environment variable is not set")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    logger.error("ACCESS_TOKEN_EXPIRE_MINUTES environment variable is not set")
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES environment variable is not set")

if not REFRESH_TOKEN_EXPIRE_DAYS:
    logger.error("REFRESH_TOKEN_EXPIRE_DAYS environment variable is not set")
    raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS environment variable is not set")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

async def cleanup_expired_tokens(db: AsyncSession):
    """Cleanup expired tokens from the blacklist"""
    try:
        # Delete tokens older than REFRESH_TOKEN_EXPIRE_DAYS
        cutoff_date = datetime.utcnow() - timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await db.execute(
            delete(TokenBlacklist).where(TokenBlacklist.blacklisted_at < cutoff_date)
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
        await db.rollback()

async def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_access_token(data: dict) -> str:
    return await create_token(
        data=data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

async def create_refresh_token(data: dict) -> str:
    return await create_token(
        data=data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def is_token_blacklisted(db: AsyncSession, token: str) -> bool:
    # Periodically cleanup expired tokens
    await cleanup_expired_tokens(db)
    
    result = await db.execute(
        select(TokenBlacklist).filter(TokenBlacklist.token == token)
    )
    return result.scalar() is not None

async def blacklist_token(db: AsyncSession, token: str):
    if not token:
        return
        
    # Check if token already blacklisted
    existing = await db.execute(
        select(TokenBlacklist).filter(TokenBlacklist.token == token)
    )
    if existing.scalar():
        return

    token_blacklist = TokenBlacklist(
        token=token,
        blacklisted_at=datetime.utcnow()
    )
    db.add(token_blacklist)
    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Error blacklisting token: {str(e)}")
        await db.rollback()

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

        # Check if user has an active session
        logged_query = await db.execute(
            select(Logged).filter(Logged.username == username)
        )
        logged_user = logged_query.scalar()
        
        if not logged_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No active session found"
            )

        if logged_user.access_token != token:
            # Token is valid but not the current one
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session has been invalidated"
            )

        # Log the types for debugging
        logger.debug(f"BusinessId type before conversion: {type(user.businessId)}, value: {user.businessId}")
        
        # Enhanced debug logging for businessId handling
        logger.debug(f"Raw businessId from database: {user.businessId}")
        if isinstance(user.businessId, list):
            logger.debug(f"BusinessId is a list: {user.businessId}")
        elif isinstance(user.businessId, str):
            logger.debug(f"BusinessId is a string, attempting to convert: {user.businessId}")
        elif isinstance(user.businessId, int):
            logger.debug(f"BusinessId is already an integer: {user.businessId}")
        else:
            logger.debug(f"BusinessId is of unexpected type: {type(user.businessId)}")

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
        logger.debug(f"Checking access for user: {current_user.user_name}")
        logger.debug(f"Current user status: {current_user.status}")
        logger.debug(f"Current user businessId: {current_user.businessId} (type: {type(current_user.businessId)})")

        if current_user.status != "active":
            logger.warning(f"User {current_user.user_name} is not active. Status: {current_user.status}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active"
            )

        # Ensure businessId is an integer
        if current_user.businessId is not None:
            try:
                current_user.businessId = int(current_user.businessId)
            except (ValueError, TypeError):
                logger.error(f"Invalid businessId format: {current_user.businessId}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Invalid businessId format"
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
    db: AsyncSession = Depends(get_db),  # Inject the db session
) -> UserRegistrationSchema:
    return await get_current_user_with_access(token, db, is_admin=True)


async def get_current_normal_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserRegistrationSchema:
    # First get the current user
    current_user = await get_current_user(token, db)
    # Then check access
    return await get_current_user_with_access(current_user, db, is_admin=False)

async def validate_password(password: str):
    if len(password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters long"
        )
    return True

