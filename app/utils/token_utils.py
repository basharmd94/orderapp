from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os
from logs import setup_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete  # Added this import
from models.users_model import TokenBlacklist

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