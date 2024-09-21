import traceback  # For detailed error logging
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import func
from controllers.db_controllers.database_controller import DatabaseController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema
from models.users_model import Prmst, ApiUsers, Logged
from utils.error import error_details
from utils.auth import create_access_token
from logs import setup_logger
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Setup logger
logger = setup_logger()


class UserRegistrationController(DatabaseController):
    """
    Controller responsible for handling user registrations.
    """

    async def check_exists(self, model, attribute, value, error_message):
        """
        Generic method to check if a record exists in the database.

        Args:
            model: SQLAlchemy model to query.
            attribute (str): Attribute of the model to filter by.
            value: Value to filter the attribute.
            error_message (str): Error message to raise if the record exists.

        Raises:
            HTTPException: If the record exists or if there's an internal error.
        """
        try:
            if not hasattr(model, attribute):
                logger.error(f"Model {model.__name__} does not have attribute '{attribute}'")
                raise ValueError(f"Invalid attribute '{attribute}' for model {model.__name__}")

            # Normalize string inputs for case-insensitive comparison
            if isinstance(value, str):
                normalized_value = value.strip().lower()
                query = select(model).filter(func.lower(getattr(model, attribute)) == normalized_value)
            else:
                normalized_value = value
                query = select(model).filter(getattr(model, attribute) == normalized_value)

            logger.debug(f"Executing query: {query}")
            result = await self.db.execute(query)
            exists = result.scalars().first()

            logger.debug(f"Result of existence check for {attribute}='{normalized_value}': {exists is not None}")
            logger.debug(f"Exists Value: {exists}")

            if exists:
                logger.error(error_message)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message,
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking existence of {attribute}: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during existence check",
            )

    async def check_user_id_in_prmst(self, user_id: str):
        """
        Check if the provided user_id exists in the Prmst table.

        Args:
            user_id (str): The employee code to verify.

        Raises:
            HTTPException: If the user_id does not exist.
        """
        try:
            normalized_user_id = user_id.strip().lower()
            logger.debug(f"Checking if user_id '{normalized_user_id}' exists in Prmst...")
            query = select(Prmst).filter(func.lower(Prmst.xemp) == normalized_user_id)
            logger.debug(f"Executing query: {query}")
            result = await self.db.execute(query)
            prmst_user = result.scalars().first()
            logger.debug(f"Result of Prmst check for xemp='{normalized_user_id}': {prmst_user is not None}")

            if not prmst_user:
                error_msg = "You have no ID in employee table"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_details(error_msg),
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking user ID in Prmst: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during user ID check",
            )

    async def check_username_exists(self, username: str):
        """
        Check if the provided username already exists.

        Args:
            username (str): The username to verify.

        Raises:
            HTTPException: If the username already exists.
        """
        await self.check_exists(
            model=ApiUsers,
            attribute='username',
            value=username,
            error_message="User Name already registered in registration table",
        )

    async def check_employeeCode_exist_in_apiusers(self, employee_code: str):
        """
        Check if the provided employee code already exists.

        Args:
            employee_code (str): The employee code to verify.

        Raises:
            HTTPException: If the employee code already exists.
        """
        await self.check_exists(
            model=ApiUsers,
            attribute='employeeCode',
            value=employee_code,
            error_message="Employee code already registered in registration table",
        )

    async def check_email_exists(self, email: str):
        """
        Check if the provided email already exists.

        Args:
            email (str): The email to verify.

        Raises:
            HTTPException: If the email already exists.
        """
        await self.check_exists(
            model=ApiUsers,
            attribute='email',
            value=email,
            error_message="Email already registered in registration table",
        )

    def hash_password(self, password: str) -> str:
        """
        Hash the provided password using the configured hashing algorithm.

        Args:
            password (str): The plaintext password.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)

    async def register_user(self, users: UserRegistrationSchema):
        """
        Register a new user after performing all necessary validations.

        Args:
            users (UserRegistrationSchema): The user registration data.

        Returns:
            ApiUsers: The newly created user.

        Raises:
            HTTPException: If any validation fails or if there's an internal error.
        """
        try:
            # Normalize input data
            normalized_username = users.user_name.strip().lower()
            normalized_email = users.email.strip().lower()
            normalized_user_id = users.user_id.strip().lower()

            logger.debug(f"Normalized Username: '{normalized_username}'")
            logger.debug(f"Normalized Email: '{normalized_email}'")
            logger.debug(f"Normalized User ID: '{normalized_user_id}'")

            # Update the users object with normalized data
            users.user_name = normalized_username
            users.email = normalized_email
            users.user_id = normalized_user_id

            # Perform all existence checks
            await self.check_user_id_in_prmst(users.user_id)
            await self.check_username_exists(users.user_name)
            await self.check_email_exists(users.email)
            await self.check_employeeCode_exist_in_apiusers(users.user_id)

            # Hash the password
            hashed_password = self.hash_password(users.password)
            logger.debug("Password hashed successfully.")

            # Convert Pydantic model to dictionary
            user_data = users.dict()
            logger.debug(f"User data before processing: {user_data}")

            # Generate accode based on business IDs
            business_ids = set(user_data.get("businessId", []))
            accode = ""
            if 100000 in business_ids:
                accode += "a"
            if 100001 in business_ids:
                accode += "b"
            if 100005 in business_ids:
                accode += "c"
            user_data["accode"] = accode
            logger.debug(f"Generated Accode: '{accode}'")

            # Ensure businessId list is not empty
            if not business_ids:
                error_msg = "At least one business ID must be provided"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_details(error_msg),
                )

            # Update user data with hashed password
            user_data["password"] = hashed_password
            user_data.pop("confirm_password", None)  # Remove confirm_password if present
            logger.debug("Updated user data with hashed password and removed confirm_password.")

            # Initialize UserDBController to get next terminal
            database_controller = UserDBController()
            await database_controller.connect()
            logger.debug("Connected to the database.")

            next_terminal = await database_controller.get_next_terminal()
            logger.debug(f"Obtained Next Terminal: '{next_terminal}'")

            # Determine user role
            is_admin_role = "admin" if user_data.get("is_admin", "").lower() == "admin" else "user"
            logger.debug(f"Determined User Role: '{is_admin_role}'")

            # Create new user instance
            new_user = ApiUsers(
                username=users.user_name,
                password=hashed_password,
                employee_name=users.user_name,
                email=users.email,
                mobile=users.mobile,
                status="inactive",
                businessId=next(iter(business_ids)),  # Get one businessId; adjust as needed
                employeeCode=users.user_id,
                terminal=next_terminal,
                is_admin=is_admin_role,
                accode=accode,  # Assuming accode is meant to be a concatenated string like 'abc'
            )
            logger.debug(f"Creating new user instance: {new_user}")

            # Add and commit the new user to the database
            self.db.add(new_user)
            logger.debug("Added new user to the database session.")
            await self.db.commit()
            logger.debug("Committed the transaction.")
            await self.db.refresh(new_user)
            logger.info(f"User '{new_user.username}' created successfully with ID {new_user.id}")

            return new_user

        except HTTPException as e:
            logger.error(f"HTTP error while registering user: {str(e)}")
            raise e
        except Exception as e:
            logger.error(
                f"Unexpected error during user registration: {str(e)}\n{traceback.format_exc()}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during user registration",
            )
        await database_controller.close()