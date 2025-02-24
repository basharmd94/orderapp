import traceback
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema, UserRegistrationResponse
from models.users_model import Prmst, ApiUsers
from utils.error import error_details
from logs import setup_logger
from passlib.context import CryptContext



# Initialize password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Setup logger
logger = setup_logger()

class UserRegistrationController:
    def __init__(self, db: AsyncSession):
        self.db = db  # Use the session passed in from the route handler
        self.user_db_controller = UserDBController(db)

    async def check_exists(self, model, attribute, value, error_message):
        try:
            if not hasattr(model, attribute):
                logger.error(f"Model {model.__name__} does not have attribute '{attribute}'")
                raise ValueError(f"Invalid attribute '{attribute}' for model {model.__name__}")

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
        await self.check_exists(
            model=ApiUsers,
            attribute='username',
            value=username,
            error_message="User Name already registered in registration table",
        )

    async def check_employeeCode_exist_in_apiusers(self, employee_code: str):
        await self.check_exists(
            model=ApiUsers,
            attribute='employeeCode',
            value=employee_code,
            error_message="Employee code already registered in registration table",
        )

    async def check_email_exists(self, email: str):
        await self.check_exists(
            model=ApiUsers,
            attribute='email',
            value=email,
            error_message="Email already registered in registration table",
        )

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def register_user(self, users: UserRegistrationSchema):
        try:
            normalized_username = users.user_name.strip().lower()
            normalized_email = users.email.strip().lower()
            normalized_user_id = users.user_id.strip().lower()

            logger.debug(f"Normalized Username: '{normalized_username}'")
            logger.debug(f"Normalized Email: '{normalized_email}'")
            logger.debug(f"Normalized User ID: '{normalized_user_id}'")

            users.user_name = normalized_username
            users.email = normalized_email
            users.user_id = normalized_user_id

            await self.check_user_id_in_prmst(users.user_id)
            await self.check_username_exists(users.user_name)
            await self.check_email_exists(users.email)
            await self.check_employeeCode_exist_in_apiusers(users.user_id)

            hashed_password = self.hash_password(users.password)
            logger.debug("Password hashed successfully.")

            user_data = users.dict()
            logger.debug(f"User data before processing: {user_data}")

            business_id = user_data.get("businessId")
            accode = ""
            if (business_id == 100000):
                accode = "a"
            elif (business_id == 100001):
                accode = "b"
            elif (business_id == 100005):
                accode = "c"
            user_data["accode"] = accode
            logger.debug(f"Generated Accode: '{accode}'")

            if not business_id:
                error_msg = "Business ID must be provided"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_details(error_msg),
                )

            user_data["password"] = hashed_password
            user_data.pop("confirm_password", None)  # Remove confirm_password if present
            logger.debug("Updated user data with hashed password and removed confirm_password.")

            user_db = UserDBController(self.db)
            next_terminal = await self.user_db_controller.get_next_terminal()

            print (users, "HERE IS BUSINESS ID")

            new_user = ApiUsers(
                username=users.user_name, 
                password=hashed_password,
                employee_name=users.user_name,
                email=users.email,
                mobile=users.mobile,
                status="inactive",
                businessId=business_id,
                employeeCode=users.user_id.upper(),
                terminal=next_terminal,
                is_admin="user",  # Changed to directly use the string value
                accode=accode,
            )
            logger.debug(f"Creating new user instance: {new_user}")

            self.db.add(new_user)
            logger.debug("Added new user to the database.")
            await self.db.commit()  # Commit the transaction
            logger.debug("Database commit successful.")

            # Return filtered response without sensitive data
            return UserRegistrationResponse.model_validate(new_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during user registration",
            )
