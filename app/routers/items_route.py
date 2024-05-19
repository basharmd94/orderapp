from fastapi import APIRouter
from logs import setup_logger
from database import get_db
from models.items_model import Base, Caitem

router = APIRouter()


@router.get("/", tags=["Items"])
async def get_all_items():
    db = next(get_db())
    items = db.query(Caitem).all()
    db.close()
    return {"items": items}
