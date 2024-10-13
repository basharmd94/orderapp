from typing import List, Union
from pydantic import BaseModel, Field


class Item(BaseModel):
    xitem: str
    xdesc: str
    xqty: int
    xprice: int
    xroword: int
    # xterminal: str
    xdate: str
    xsl: str
    xlat: Union[float, None] = Field(default=None)
    xlong: Union[float, None] = Field(default=None)
    xlinetotal: int



class OpmobSchema(BaseModel):
    # invoiceno: str
    # invoicesl: int
    # username: str
    # xemp: str
    xcus: str
    xcusname: str
    xcusadd: str
    items: List[Item]


