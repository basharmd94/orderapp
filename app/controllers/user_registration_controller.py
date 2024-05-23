# controllers/user_registration_controller.py
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

    def check_user_is_active(self, user_id: str):
        user_is_active = self.db.query(Prmst).filter_by(xemp=user_id).first()
        if user_is_active is None or user_is_active.xstatusemp != "A-Active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details(
                    "Your ID has been deactivated or blank status in employee table"
                ),
            )

    def check_username_exists(self, username: str):
        if self.db.query(ApiUsers).filter(ApiUsers.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details(
                    "User Name already registered in registration table"
                ),
            )

    def check_employeeCode_exist_in_apiusers(self, user_id: str):
        if self.db.query(ApiUsers).filter(ApiUsers.employeeCode == user_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details(
                    "Employee code already registered in registration table"
                ),
            )

    def check_email_exists(self, email: str):
        if self.db.query(ApiUsers).filter(ApiUsers.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details("Email already registered in registration table"),
            )

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def register_user(self, users: UserRegistrationSchema):
        self.check_user_id_in_prmst(users.user_id)
        self.check_user_is_active(users.user_id)
        self.check_username_exists(users.user_name)
        self.check_email_exists(users.email)
        self.check_employeeCode_exist_in_apiusers(users.user_id)

        hashed_password = self.hash_password(users.password)
        user_data = users.dict()
        # print(user_data)
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
            status=users.status,
            businessId=users.businessId,
            employeeCode=users.user_id,
            terminal=next_terminal,
            is_admin="is_admin" if user_data["is_admin"] == "abcdefgh" else "None",
            accode=users.accode,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # access_token_data = {
        #     "username": new_user.username,
        #     "accode": new_user.accode,
        #     "status": new_user.status,
        #     "user_id": new_user.employeeCode,
        #     "is_admin": new_user.is_admin
        # }
        # access_token = create_access_token(data=access_token_data)

        # refresh_token_data = {
        #     "username": new_user.username,
        #     "accode": new_user.accode,
        #     "status": new_user.status,
        #     "user_id": new_user.employeeCode,
        #     "is_admin": new_user.is_admin
        # }
        # refresh_token = create_refresh_token(data=refresh_token_data)

        # logged_user = Logged(
        #     username=new_user.username,
        #     businessId=new_user.businessId,
        #     access_token=access_token,
        #     refresh_token=refresh_token,
        #     status="Logged In"
        # )
        # self.db.add(logged_user)
        # self.db.commit()
        # self.db.refresh(logged_user)

        return new_user
