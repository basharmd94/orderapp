from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/da"

# Create an asynchronous engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Dependency
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
