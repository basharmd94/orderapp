from typing import List, Union
from pydantic import BaseModel, Field


class Item(BaseModel):
    xitem: str
    xdesc: str
    xqty: int
    xprice: int
    # xstatusord: Union[str, None] = Field(default=None)
    # xordernum: Union[str, None] = Field(default=None)
    xroword: int
    # xterminal: str
    xdate: str
    xsl: str
    xlat: Union[float, None] = Field(default=None)
    xlong: Union[float, None] = Field(default=None)
    xlinetotal: int
    # xtra1: Union[int, None] = Field(default=None)
    # xtra2: float
    # xtra3: Union[str, None] = Field(default=None)
    # xtra4: Union[str, None] = Field(default=None)
    # xtra5: Union[str, None] = Field(default=None)


class OpmobSchema(BaseModel):
    # invoiceno: str
    # invoicesl: int
    # username: str
    # xemp: str
    xcus: str
    xcusname: str
    xcusadd: str
    items: List[Item]
