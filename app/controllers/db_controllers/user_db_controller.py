from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from models.users_model import ApiUsers
from controllers.db_controllers.database_controller import DatabaseController
from sqlalchemy.ext.asyncio import AsyncSession

class UserDBController:

    def __init__(self, db: AsyncSession):
        self.db = db  # Use the session passed in from the route handler

    """Controller for handling user-related database operations."""
 
    async def get_user_by_username(self, username: str) -> ApiUsers:
        """
        Fetch a user by their username.

        :param username: The username of the user.
        :return: An instance of ApiUsers or None if not found.
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Construct the select query
        query = select(ApiUsers).filter(ApiUsers.username == username)
        
        # Execute the query
        result = await self.db.execute(query)
        
        # Return the first result or None
        return result.scalars().first()  # Return the first result or None
 
    async def get_user_by_id(self, user_id: str) -> ApiUsers:
        """
        Fetch a user by their ID.

        :param user_id: The ID of the user.
        :return: An instance of ApiUsers or None if not found.
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Construct the select query
        query = select(ApiUsers).filter(ApiUsers.employeeCode == user_id)
        
        # Execute the query
        result = await self.db.execute(query)
        
        # Return the first result or None
        return result.scalars().first()  # Return the first result or None
    async def get_all_users(self) -> list[ApiUsers]:
        """
        Fetch all users from the ApiUsers table.

        :return: A list of ApiUsers instances.
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Construct the select query
        query = select(ApiUsers)
        
        # Execute the query
        result = await self.db.execute(query)
        
        # Return all results as a list
        return result.scalars().all()  # Return all results as a list


    async def get_next_terminal(self) -> str:
        """
        Fetch the last terminal from ApiUsers, increment it by one, and return the new terminal number.

        :return: The next terminal number as a string.
        """
        if self.db is None:
            raise Exception("Database session not initialized.")

        async with self.db.begin_nested():  # Use begin_nested() to create a sub-transaction
            # Lock the table to prevent race conditions
            query = select(ApiUsers).with_for_update().order_by(ApiUsers.terminal.desc())
            result = await self.db.execute(query)
            last_terminal_user = result.scalars().first()

            if last_terminal_user and last_terminal_user.terminal:
                last_terminal = last_terminal_user.terminal
                # Extract numeric part from the terminal (assuming the format is T0001, T0002, etc.)
                terminal_number = int(last_terminal[1:])
                # Increment the number
                new_terminal_number = terminal_number + 1
                # Format the new terminal (e.g., T0002)
                new_terminal = f"T{new_terminal_number:04d}"
            else:
                # Default starting terminal if no terminals are found
                new_terminal = "T0001"

        return new_terminal


