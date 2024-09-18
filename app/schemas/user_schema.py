from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ValidationError,
    field_validator,
    model_validator,
)
from typing import Union
from passlib.context import CryptContext
from typing_extensions import Self
from utils.examples import (
    registration_example,
)  # Assuming this imports the examples correctly

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserBaseSchema(BaseModel):
    user_id: str = Field(..., min_length=6)
    user_name: str = Field(..., min_length=3)
    mobile: str = Field(..., max_length=11)  # Consider a stricter mobile validation
    email: str
    # status: Union[str, None] = Field(default="inactive", title="default is active")
    businessId: list[int] = Field([], title="list of businessId")
    # terminal: Union[str, None] = None
    # accode: Union[str, None] = Field(default=0)
    is_admin: Union[str, None] = None

    @field_validator("user_name")
    @classmethod
    def no_spaces(cls, v):
        if " " in v:
            raise ValueError("Spaces are not allowed in user name")
        return v

    class Config:

        json_schema_extra = {
            "examples": [
                {
                    "user_id": "IT--000009",
                    "user_name": "basharmd95",
                    "mobile": "01675373799",
                    "email": "mat197195@gmail.com",
                    "businessId": [100001, 100005, 100000],
                    "is_admin": "",
                    "password": "12345678",
                    "confirm_password": "12345678",

                }
            ]
        }


class UserRegistrationSchema(UserBaseSchema):
    password: str = Field(default="12345678", min_length=8)
    confirm_password: str = Field(default="12345678", min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @classmethod
    def hash_password(cls, password: str):
        return pwd_context.hash(password)

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: str
    password: str



class UserOutSchema(BaseModel):
    id: int
    username: Union[str, None]
    email: Union[str, None]
    status: Union[str, None]
    mobile: Union[str, None]
    employeeCode: Union[str, None]
    accode: Union[str, None]
    class Config:
        from_attributes = True  # Allows the model to work with ORM models