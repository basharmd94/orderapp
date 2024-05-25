from pydantic import BaseModel
from typing import List, Union

class CustomersSchema(BaseModel):

    zid: int
    xcus: str
    xorg: str
    xadd1: str
    xcity: str
    xstate: str
    xmobile: str
    xtaxnum: str
    xsp: Union[List[str]] = []

    class Config:
        from_attributes = True

