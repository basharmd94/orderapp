from pydantic import BaseModel, validator
from typing import List
from passlib.context import CryptContext
from typing import Union

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserBase(BaseModel):
    username: str  # Changed from user_name to username to match database model
    email: Union[str, None] = None
    mobile: Union[str, None] = None
    status: Union[str, None] = "active"
    businessId: Union[int, None] = None
    terminal: Union[str, None] = None
    accode: Union[str, None] = None
    is_admin: Union[str, None] = "user"  # Changed from bool to str with default "user"
    employee_name: Union[str, None] = None

    @validator('businessId', pre=True)
    def validate_business_id(cls, v):
        if v is None:
            return None
        if isinstance(v, (str, int)):
            try:
                return int(v)
            except (ValueError, TypeError):
                raise ValueError('businessId must be a valid integer')
        if isinstance(v, list):
            if not v:
                return None
            try:
                return int(v[0])
            except (ValueError, TypeError):
                raise ValueError('businessId must be a valid integer')
        raise ValueError('businessId must be a valid integer')

    @validator('is_admin')
    def validate_is_admin(cls, v):
        if v not in ['admin', 'user', '']:
            raise ValueError('is_admin must be either "admin", "user", or empty string')
        return v

    class Config:
        from_attributes = True

class UserRegistrationSchema(UserBase):
    password: str
    confirm_password: Union [str, None] = None
    user_id: Union [str, None] = None

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v is not None and values['password'] != v:
            raise ValueError('Passwords do not match')
        return v

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "user_id": "IT--000010",
                    "username": "basharmd91",
                    "mobile": "01675373799",
                    "email": "mat197197@gmail.com",
                    "status": "active",
                    "businessId": 100001,
                    "accode": "0",
                    "is_admin": "",
                    "password": "1234",
                    "confirm_password": "1234",
                    "terminal": "",
                }
            ]
        }

class UserOutSchema(UserBase):
    user_id: str
    businessId: int  # Changed to accept single integer

    @validator('businessId', pre=True)
    def validate_business_id(cls, v):
        if isinstance(v, list):
            # If it's a list, take the first value
            return v[0] if v else None
        return v
    
    @validator('is_admin')
    def validate_is_admin(cls, v):
        if v not in ['admin', 'user', '']:
            raise ValueError('is_admin must be either "admin", "user", or empty string')
        return v
    
    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Union [str, None] = None
    expires_in: Union [str, None] = None

class TokenPayload(BaseModel):
    username:  Union [str, None] = None
    exp: Union [int, None] = None

class UserRegistrationResponse(BaseModel):
    username: str
    email: str
    mobile: Union [str, None] = None
    status: str
    businessId: int
    employeeCode: str
    terminal: str
    is_admin: str
    id: int

    class Config:
        from_attributes = True