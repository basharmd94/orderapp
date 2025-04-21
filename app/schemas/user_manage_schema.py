from pydantic import BaseModel, EmailStr, field_validator
from typing import Union, Optional

class UserStatusUpdate(BaseModel):
    username: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "status": "active"  # or "inactive"
            }
        }

class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    mobile: Optional[str] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    businessId: Optional[int] = None
    is_admin: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator('status')
    def validate_status(cls, v):
        if v and v not in ['active', 'inactive']:
            raise ValueError('Status must be either "active" or "inactive"')
        return v

    @field_validator('is_admin')
    def validate_is_admin(cls, v):
        if v and v not in ['admin', 'user']:
            raise ValueError('is_admin must be either "admin" or "user"')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "mobile": "1234567890",
                "user_id": "WA--000003",
                "status": "active",
                "businessId": 100001,
                "is_admin": "user",
                "password": "new_password"
            }
        }