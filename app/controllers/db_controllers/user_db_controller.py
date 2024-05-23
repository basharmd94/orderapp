from sqlalchemy import func
from sqlalchemy.orm import Session
from models.users_model import ApiUsers
from controllers.db_controllers.database_controller import DatabaseController

class UserDBController(DatabaseController):
    """Controller for handling user-related database operations."""

    def get_user_by_username(self, username: str) -> ApiUsers:
        """
        Fetch a user by their username.

        :param username: The username of the user.
        :return: An instance of ApiUsers or None if not found.
        """
        return self.db.query(ApiUsers).filter(ApiUsers.username == username).first()


    def get_user_by_id(self, user_id: str) -> ApiUsers:
        """
        Fetch a user by their ID.

        :param user_id: The ID of the user.
        :return: An instance of ApiUsers or None if not found.
        """
        return self.db.query(ApiUsers).filter(ApiUsers.employeeCode == user_id).first()

    def get_next_terminal(self) -> str:
        """
        Fetch the last terminal from ApiUsers, increment it by one, and return the new terminal number.

        :return: The next terminal number as a string.
        """
        with self.db.begin_nested():  # Use begin_nested() to create a sub-transaction
            # Lock the table to prevent race conditions
            last_terminal_user = (
                self.db.query(ApiUsers)
                .with_for_update()  # Lock the selected rows for update
                .order_by(ApiUsers.terminal.desc())
                .first()
            )

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
