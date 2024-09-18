import traceback  # Added for detailed error logging
from fastapi import HTTPException, status
from controllers.db_controllers.database_controller import DatabaseController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_schema import UserRegistrationSchema
from models.users_model import Prmst, ApiUsers, Logged
from utils.error import error_details
from utils.auth import create_access_token
from logs import setup_logger
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

logger = setup_logger()


class UserRegistrationController(DatabaseController):

    def check_user_id_in_prmst(self, user_id: str):
        prmst_user = self.db.query(Prmst).filter(Prmst.xemp == user_id).first()
        if not prmst_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details("You have no ID in employee table"),
            )

    def check_username_exists(self, username: str):
        if self.db.query(ApiUsers).filter(ApiUsers.username == username).first():
            logger.error("User Name already registered in registration table")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details(
                    "User Name already registered in registration table"
                ),
            )

    def check_employeeCode_exist_in_apiusers(self, user_id: str):
        if self.db.query(ApiUsers).filter(ApiUsers.employeeCode == user_id).first():
            logger.error("Employee code already registered in registration table")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details(
                    "Employee code already registered in registration table"
                ),
            )

    def check_email_exists(self, email: str):
        if self.db.query(ApiUsers).filter(ApiUsers.email == email).first():
            logger.error("Email already registered in registration table")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details("Email already registered in registration table"),
            )

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def register_user(self, users: UserRegistrationSchema):
        try:
            self.check_user_id_in_prmst(users.user_id)
            self.check_username_exists(users.user_name)
            self.check_email_exists(users.email)
            self.check_employeeCode_exist_in_apiusers(users.user_id)

            hashed_password = self.hash_password(users.password)
            user_data = users.dict()

            business_ids = set(user_data["businessId"])
            accode = ""
            if 100000 in business_ids:
                accode += "a"
            if 100001 in business_ids:
                accode += "b"
            if 100005 in business_ids:
                accode += "c"
            user_data["accode"] = accode

            user_data["password"] = hashed_password
            user_data["confirm_password"] = hashed_password

            database_controller = UserDBController()
            next_terminal = database_controller.get_next_terminal()

            new_user = ApiUsers(
                username=users.user_name,
                password=hashed_password,
                employee_name=users.user_name,
                email=users.email,
                mobile=users.mobile,
                status="inactive",
                businessId=users.businessId[0],
                employeeCode=users.user_id,
                terminal=next_terminal,
                is_admin="is_admin" if user_data["is_admin"] == "admin" else "user",
                accode=",".join([str(b) for b in user_data["businessId"]]),
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            logger.info(f"{new_user} created successfully")

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
