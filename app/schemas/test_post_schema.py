from pydantic import BaseModel
from typing import Union
from datetime import datetime

class AbdefSchema(BaseModel):
    xtitleord: str
    xtitledor: str
    xtitleinv: str
    xtitlerec: str
    xtitleart: str

    class Config:
        from_attributes = True
