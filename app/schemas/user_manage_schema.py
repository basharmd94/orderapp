from pydantic import BaseModel
from typing import Union

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