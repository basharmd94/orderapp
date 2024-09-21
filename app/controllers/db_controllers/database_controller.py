from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

class DatabaseController:
    def __init__(self):
        self.db: AsyncSession = None  # Initialize with None

    async def connect(self):
        async for session in get_db():
            self.db = session  # Get the session from the async generator
            break  # Exit after getting the first session

    async def close(self):
        if self.db:
            await self.db.close()  # Close the session
