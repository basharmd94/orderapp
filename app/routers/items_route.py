from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Union, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.db_controllers.items_db_controller import ItemsDBController
from schemas.items_schema import ItemsSchema, ItemsBaseSchema
from logs import setup_logger
from utils.auth import get_current_user, get_current_admin, get_current_normal_user
from schemas.user_schema import UserRegistrationSchema

router = APIRouter()
logger = setup_logger()


@router.get(
    "/all/{zid}", response_model=Union[List[ItemsSchema], List[ItemsBaseSchema]]
)
async def get_all_items(
    request: Request,
    zid: int,
    item_name: Annotated[Union[str, None], Query(description="Optional: Put Items ID or Items Name to filter results")] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    logger.info(f"get all items endpoint called: {request.url.path}")
    items_db_controller = ItemsDBController(db)
    
    items = await items_db_controller.get_all_items(
        zid=zid, item_name=item_name, limit=limit, offset=offset
    )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No items found"),
        )
    return items


