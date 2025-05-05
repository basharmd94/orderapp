from pydantic import BaseModel, Field
from typing import Optional


class ItemsBaseSchema(BaseModel):
    zid: int
    item_id: str
    item_name: str
    item_group: str
    std_price: float
    stock: float
    xbin: Optional[str] = None  # Changed to Optional[str] for product image

    class Config:
        from_attributes = True


class ItemsSchema(ItemsBaseSchema):
    min_disc_qty: float
    disc_amt: float

    class Config:
        from_attributes = True
