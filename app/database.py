from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
 

 
# Database URL
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/da"

# Create an asynchronous engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

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