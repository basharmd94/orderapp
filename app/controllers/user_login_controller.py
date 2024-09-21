from fastapi import HTTPException, status, Form
from controllers.db_controllers.database_controller import DatabaseController
from models.users_model import ApiUsers, Logged
from fastapi.security import OAuth2PasswordRequestForm
from utils.error import error_details
from utils.auth import create_access_token
from logs import setup_logger
from passlib.context import CryptContext
from sqlalchemy.future import select

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

logger = setup_logger()

class UserLoginController(DatabaseController):  
    
    async def user_login(self, form_data: OAuth2PasswordRequestForm = Form(...)):
        if self.db is None:
            raise Exception("Database session not initialized." , self.db.connection)
        logged_user = await self.db.execute(select(Logged).filter_by(username=form_data.username))
        logged_user = logged_user.scalars().first()

        if logged_user and logged_user.status == "Logged In":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_details("User already logged in"),
            )

        user = (
            await self.db.execute(select(ApiUsers).filter_by(username=form_data.username))
        )
        user = user.scalars().first()

        # If user is none and not match password
        if not user or not self.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        # If user not active in apiusers table then raise exception
        if user.status != "active":
            logger.error(f"User {user.username} not active in apiusers table")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active"
            )

        access_token_data = {
            "username": user.username,
            "accode": user.accode,
            "status": user.status,
            "user_id": user.id,
            "is_admin": user.is_admin,
        }
        access_token = await create_access_token(data=access_token_data)

        new_logged_user = Logged(
            username=user.username,
            businessId=user.businessId,
            access_token=access_token,
            refresh_token=access_token,
            status="Logged In",
        )
        self.db.add(new_logged_user)
        await self.db.commit()
        await self.db.refresh(new_logged_user)

        return {"access_token": access_token, "token_type": "bearer"}

    async def user_logout_control(self, current_user_name: str):
        logged_user = (
            await self.db.execute(select(Logged).filter_by(username=current_user_name))
        )
        logged_user = logged_user.scalars().first()

        if not logged_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not logged in"
            )

        await self.db.delete(logged_user)
        await self.db.commit()
        return {"detail": "User logged out successfully"}
        
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
