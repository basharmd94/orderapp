from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import urllib.parse
from dotenv import load_dotenv
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment or use hardcoded value as fallback
db_url = os.getenv("DATABASE_URL")

# Function to clean and validate database URL
def clean_database_url(url):
    if not url:
        return None
    
    # Fix common escape sequences
    if '\\x3a' in url:
        url = url.replace('\\x3a', ':')
    
    # Handle other common escape sequences
    for char in ['@', '/', '?', '=', '&']:
        escaped = f'\\x{ord(char):02x}'
        if escaped in url:
            url = url.replace(escaped, char)
    
    # Ensure URL is properly formatted
    if not (url.startswith('postgresql') or url.startswith('postgresql+asyncpg')):
        logger.warning(f"Invalid database URL format: {url}")
        return None
    
    # Try to parse the URL to validate it
    try:
        parts = urllib.parse.urlparse(url)
        if not all([parts.scheme, parts.netloc]):
            logger.warning(f"Invalid database URL structure: {url}")
            return None
        
        logger.info(f"Successfully validated database URL with scheme: {parts.scheme}")
        return url
    except Exception as e:
        logger.error(f"Error parsing database URL: {str(e)}")
        return None

# Clean and validate the database URL
cleaned_url = clean_database_url(db_url)

# Use cleaned value or default if environment variable is invalid
SQLALCHEMY_DATABASE_URL = cleaned_url if cleaned_url else "postgresql+asyncpg://postgres:postgres@localhost:5432/da"

logger.info(f"Using database URL with scheme: {SQLALCHEMY_DATABASE_URL.split('://')[0]}")

# Create an asynchronous engine with properly configured connection pool
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_size=5,  # Set a reasonable pool size
    max_overflow=10,  # Allow up to 10 connections beyond pool_size when needed
    pool_timeout=30,  # Wait up to 30 seconds for a connection before timing out
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True  # Verify connections are still valid before using them
)

# Create session maker
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for declarative models
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as db:
        try:
            yield db
        finally:
            await db.close()