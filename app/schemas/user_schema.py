from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    model_validator,
    ValidationError,
    field_validator,
)
from typing import Union
from typing_extensions import Self
from passlib.context import CryptContext
from utils.examples import registration_example


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserBaseSchema(BaseModel):
    user_id: str = Field(..., min_length=6)
    user_name: str = Field(..., min_length=3)
    mobile: str = Field(..., max_length=11)
    email: EmailStr
    status: Union[str, None] = Field(default="active", title="default is active")
    businessId: int
    terminal: str
    accode: Union[str, None] = Field(default=0)
    is_admin: Union[str, None] = None

    @field_validator("user_name")
    @classmethod
    def no_spaces(cls, v):
        if " " in v:
            raise ValueError("Spaces are not allowed in user name")
        return v

    model_config = registration_example


class UserRegistrationSchema(UserBaseSchema):
    password: str = Field(default="12345678", min_length=8)
    confirm_password: str = Field(default="12345678", min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self

    @classmethod
    def hash_password(cls, password: str):
        return pwd_context.hash(password)

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: str
    password: str
