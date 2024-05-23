from fastapi import HTTPException, Depends, status, Request
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from schemas.user_schema import UserRegistrationSchema
from models.users_model import ApiUsers
from controllers.db_controllers.user_db_controller import UserDBController


SECRET_KEY = "f1b2437d4edb14f189fab6821e7d8855b4e702ae169eb391232131da260a9f2b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# def create_refresh_token(data: dict):
#     expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     data.update({"exp": expire})
#     encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), ) -> UserRegistrationSchema:
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
    except jwt.JWTError:
        raise credentials_exception

    database_controller = UserDBController()
    user = database_controller.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return UserRegistrationSchema(
        user_id=user.employeeCode,
        user_name=user.username,
        mobile=user.mobile,
        email=user.email,
        status=user.status,
        businessId=user.businessId,
        terminal=user.terminal,
        accode=user.accode,
        is_admin=user.is_admin
    )


def get_current_user_with_access(request: Request, token: str = Depends(oauth2_scheme), is_admin: bool = False) -> UserRegistrationSchema:
    database_controller = UserDBController()
    user = get_current_user(token)
    
    # Fetch the user status from the database

    user_db = database_controller.get_user_by_id(user.user_id)
    
    if user_db.status != "active":
        # Blacklist user logic here if needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    path = str(request.url.path)
    print(path)  # Debugging line to print the URL path

    url_route = database_controller.get_urlroute_by_path(path)
    if not url_route:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No route found for the path")

    accodes = url_route.acodes.split(',')

    # Check if user is admin or user.accode is in the accodes list
    if is_admin and user_db.is_admin != "is_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    if user_db.accode not in accodes and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access not allowed")

    return user

def get_current_admin(request: Request, token: str = Depends(oauth2_scheme)) -> UserRegistrationSchema:
    return get_current_user_with_access(request, token, is_admin=True)

def get_current_normal_user(request: Request, token: str = Depends(oauth2_scheme)) -> UserRegistrationSchema:
    return get_current_user_with_access(request, token, is_admin=False)