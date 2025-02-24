from pydantic import BaseModel
from typing import List, Optional

class CustomersSchema(BaseModel):
    zid: int
    xcus: str
    xorg: str
    xadd1: str
    xcity: str
    xstate: str
    xmobile: str
    xtaxnum: str
    xsp: Optional[str] = None
    xsp1: Optional[str] = None
    xsp2: Optional[str] = None
    xsp3: Optional[str] = None

    class Config:
        from_attributes = True

