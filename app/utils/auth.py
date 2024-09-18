from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from schemas.user_schema import UserRegistrationSchema
from models.users_model import ApiUsers
from controllers.db_controllers.user_db_controller import UserDBController

"""
This module contains the code for authentication using JWT.

The process of authentication is as follows:
1. The user provides their username and password in the request body.
2. The server checks if the username and password are correct.
3. If the username and password are correct, the server generates a JWT token.
4. The server returns the JWT token to the user.
5. The user includes the JWT token in the Authorization header of their requests.
6. The server verifies the JWT token and checks if it is valid.
7. If the JWT token is valid, the server returns the response to the user.

The code is organized as follows:
1. The `UserDBController` class is used to interact with the database, specifically to get the user by their username and password.
2. The `pwd_context` object is used to hash the password.
3. The `oauth2_scheme` object is used to define the OAuth2 password flow.
4. The `SECRET_KEY` and `ALGORITHM` constants are used to generate the JWT token.
5. The `create_access_token` function is used to generate the JWT token.
6. The `get_current_user` function is used to get the current user from the JWT token.

The code is tested using Pytest.
"""

SECRET_KEY = "f1b2437d4edb14f189fab6821e7d8855b4e702ae169eb391232131da260a9f2b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # print(data, "in auth.py")
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


def get_current_user(
    token: str = Depends(oauth2_scheme),
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
    except jwt.JWTError:
        raise credentials_exception

    database_controller = UserDBController()
    user = database_controller.get_user_by_username(username)
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


def get_current_user_with_access(
    token: str = Depends(oauth2_scheme), is_admin: bool = False
) -> UserRegistrationSchema:
    database_controller = UserDBController()
    user = get_current_user(token)
    

    # Fetch the user status from the database

    user_db = database_controller.get_user_by_id(user.user_id)

    if user_db.status != "active":
        # Blacklist user logic here if needed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active"
        )

    # print(request.query_params['search'])  # Debugging line to print the URL path

    # Check if user is admin or user.accode is in the accodes list
    if is_admin and user_db.is_admin != "is_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return user


def get_current_admin(token: str = Depends(oauth2_scheme)) -> UserRegistrationSchema:
    return get_current_user_with_access(token, is_admin=True)

def get_current_normal_user(
    token: str = Depends(oauth2_scheme),
) -> UserRegistrationSchema:
    return get_current_user_with_access(token, is_admin=False)
