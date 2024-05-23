# controllers/user_login_controller.py
from fastapi import HTTPException, status, Form
from controllers.db_controllers.database_controller import DatabaseController
from models.users_model import ApiUsers, Logged
from fastapi.security import OAuth2PasswordRequestForm
from utils.error import error_details
from utils.auth import create_access_token
from logs import setup_logger
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

logger = setup_logger()


class UserLoginController(DatabaseController):
    async def user_login(self, form_data: OAuth2PasswordRequestForm = Form(...)):
        logged_user = self.db.query(Logged).filter_by(
            username=form_data.username).first()
        if logged_user and logged_user.status == "Logged In":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_details(
                    "User already logged in")
            )

        user = self.db.query(ApiUsers).filter_by(
            username=form_data.username).first()

        if not user or not self.verify_password(form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password")

        access_token_data = {
            "username": user.username,
            "accode": user.accode,
            "status": user.status,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
        access_token = create_access_token(data=access_token_data)

        # refresh_token_data = {
        #     "username": user.username,
        #     "accode": user.accode,
        #     "status": user.status,
        #     "user_id": user.id,
        #     "is_admin": user.is_admin
        # }
        # refresh_token = create_refresh_token(data=refresh_token_data)

        new_logged_user = Logged(
            username=user.username,
            businessId=user.businessId,
            access_token=access_token,
            refresh_token=access_token,
            status="Logged In"
        )
        self.db.add(new_logged_user)
        self.db.commit()
        self.db.refresh(new_logged_user)

        return {"access_token": access_token, "token_type": "bearer"}

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
