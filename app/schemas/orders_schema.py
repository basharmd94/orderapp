from typing import List, Union, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Item(BaseModel):
    xitem: str
    xdesc: str
    xqty: int
    xprice: float  # Changed from int to float
    xroword: int
    xdate: str
    xsl: str
    xlat: Union[float, None] = Field(default=None)
    xlong: Union[float, None] = Field(default=None)
    xlinetotal: float  # Changed from int to float to handle decimal prices


class OpmobSchema(BaseModel):
    zid: int = Field(..., gt=0, description="The ID of the Business")
    xcus: str
    xcusname: str
    xcusadd: str
    items: List[Item]


class OpmobResponse(BaseModel):
    invoicesl: int
    xroword: int
    zutime: datetime
    xdate: datetime
    xqty: int
    xlat: Optional[float] = None
    xlong: Optional[float] = None
    xlinetotal: float  # Changed to float
    xtra1: Optional[int] = None
    xtra2: Optional[float] = None
    xprice: float
    ztime: datetime
    zid: int
    xtra3: Optional[str] = None
    xtra4: Optional[str] = None
    xtra5: Optional[str] = None
    invoiceno: str
    username: str
    xemp: str
    xcus: str
    xcusname: str
    xcusadd: str
    xitem: str
    xdesc: str
    xstatusord: Optional[str] = None
    xordernum: Optional[str] = None
    xterminal: str
    xsl: str

    class Config:
        from_attributes = True

class BulkOpmobSchema(BaseModel):
    orders: List[OpmobSchema]

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "orders": [
                        {
                            "zid": 100000,
                            "xcus": "CUS-000001",
                            "xcusname": "Fixit Gulshan",
                            "xcusadd": "Customer Address 1",
                            "items": [
                                {
                                    "xitem": "CF000003",
                                    "xdesc": "korean putty",
                                    "xqty": 10,
                                    "xprice": 100,
                                    "xroword": 1,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": 23.8103,
                                    "xlong": 90.4125,
                                    "xlinetotal": 1000
                                },
                                {
                                    "xitem": "CF000002",
                                    "xdesc": "Damp crush",
                                    "xqty": 5,
                                    "xprice": 200,
                                    "xroword": 2,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": None,
                                    "xlong": None,
                                    "xlinetotal": 1000
                                },
                            ]
                        },
                        {
                            "zid": 100005,
                            "xcus": "CUS-000002",
                            "xcusname": "Fixit Gulshan",
                            "xcusadd": "Customer Address 2",
                            "items": [
                                {
                                    "xitem": "CF000001",
                                    "xdesc": "Draino Powder",
                                    "xqty": 5,
                                    "xprice": 200,
                                    "xroword": 2,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": None,
                                    "xlong": None,
                                    "xlinetotal": 1000
                                },
                                {
                                    "xitem": "CF000004",
                                    "xdesc": "Clean x 1 litre",
                                    "xqty": 5,
                                    "xprice": 200,
                                    "xroword": 2,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": None,
                                    "xlong": None,
                                    "xlinetotal": 1000
                                },
                                {
                                    "xitem": "CF000005",
                                    "xdesc": "Pliers 5 inch",
                                    "xqty": 5,
                                    "xprice": 300,
                                    "xroword": 2,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": None,
                                    "xlong": None,
                                    "xlinetotal": 1000
                                },
                                ### add more items below
                                {
                                    "xitem": "CF000006",
                                    "xdesc": "Screwdriver 10 inch",
                                    "xqty": 5,
                                    "xprice": 400,
                                    "xroword": 2,
                                    "xdate": "2023-10-01",
                                    "xsl": "some-string",
                                    "xlat": None,
                                    "xlong": None,
                                    "xlinetotal": 2000
                                }

                            ]
                        }
                    ]
                },
            ]
        }
