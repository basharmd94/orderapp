
from models.users_model import ApiUsers, Prmst
from controllers.db_controllers.database_controller import DatabaseController

class TestDbController(DatabaseController):
    """Controller for handling user-related database operations."""

    async def get_all_users(self) -> list[ApiUsers]:
        """
        Fetch all users from the database.

        :return: A list of ApiUsers instances.
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        result = await self.db.execute(select(ApiUsers))
        return result.scalars().all()  # Return all results as a list
