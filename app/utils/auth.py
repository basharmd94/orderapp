# auth.py
import traceback
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from schemas.user_schema import UserRegistrationSchema
from models.users_model import ApiUsers
from controllers.db_controllers.user_db_controller import UserDBController
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from logs import setup_logger

SECRET_KEY = "f1b2437d4edb14f189fab6821e7d8855b4e702ae169eb391232131da260a9f2b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
logger = setup_logger()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)  # Correctly inject AsyncSession here
) -> UserRegistrationSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except JWTError:
        raise credentials_exception

    database_controller = UserDBController(db)  # Pass the db session here
    
    try:
        user = await database_controller.get_user_by_username(username)
        if user is None:
            raise credentials_exception

        # Ensure businessId is a list
        business_ids = (
            [user.businessId] if isinstance(user.businessId, int) else user.businessId
        )

        return UserRegistrationSchema(
            user_id=user.employeeCode,
            user_name=user.username,
            mobile=user.mobile,
            email=user.email,
            status=user.status,
            businessId=business_ids,
            terminal=user.terminal,
            accode=user.accode,
            is_admin=user.is_admin,
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during get user: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def get_current_user_with_access(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # Inject the db session correctly
    is_admin: bool = False
) -> UserRegistrationSchema:
    user = await get_current_user(token, db)  # Pass db session here
    database_controller = UserDBController(db)
    
    try:
        # Fetch the user status from the database
        user_db = await database_controller.get_user_by_id(user.user_id)

        if user_db.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
            )

        if is_admin and user_db.is_admin != "is_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        return user
    except Exception as e:
        logger.error(
            f"Unexpected error during user access check: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # Inject the db session
) -> UserRegistrationSchema:
    return await get_current_user_with_access(token, db, is_admin=True)


async def get_current_normal_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # Inject the db session
) -> UserRegistrationSchema:
    return await get_current_user_with_access(token, db, is_admin=False)
    
