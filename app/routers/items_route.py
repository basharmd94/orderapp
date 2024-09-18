from fastapi import APIRouter, HTTPException, status, Path, Depends, Query, Request
from logs import setup_logger
from database import get_db
from models.items_model import Base, Caitem
from schemas.items_schema import ItemsBaseSchema, ItemsSchema
from schemas.user_schema import UserRegistrationSchema
from controllers.db_controllers.items_db_controller import ItemsDBController
from typing import List, Union
from utils.error import error_details
from typing_extensions import Annotated
from utils.auth import get_current_user, get_current_admin, get_current_normal_user

router = APIRouter()
logger = setup_logger()


items_db_controller = ItemsDBController()


@router.get(
    "/all/{zid}", response_model=Union[List[ItemsSchema], List[ItemsBaseSchema]]
)
async def get_all_items(
    request: Request,
    zid: int,
    item: Annotated[str, Query(min_length=3, description="Put Items ID or Items Name")],
    limit: int = 10,
    offset: int = 0,
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    # print(current_user.terminal)
    current_user_acccode = current_user.accode
    logger.info(f"get all items endpoint called: {request.url.path}")
    print(current_user_acccode, "item_route")


    if zid in [100000, 100001]:
        items = items_db_controller.get_all_items(
            zid=zid, item_name=item, limit=limit, offset=offset
        )
        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_details("No items found"),
            )
        return items

    items = items_db_controller.get_all_items_exclude_hmbr(
        zid=zid, item_name=item, limit=limit, offset=offset
    )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No items found"),
        )
    return items



@router.get(
    "/items_without_auth", response_model=Union[List[ItemsSchema], List[ItemsBaseSchema]]
)
async def items_without_auth(
    request: Request,
    zid: int,
    item: str = Query(..., min_length=3, description="Put Items ID or Items Name"),
    limit: int = 10,
    offset: int = 0,
    
):
    """
    Route to get items without requiring authentication.
    """
    logger.info(f"get all items endpoint called: {request.url.path}")

    if zid in [100000, 100001]:
        items = items_db_controller.get_all_items(
            zid=zid, item_name=item, limit=limit, offset=offset
        )
        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_details("No items found"),
            )
        return items

    items = items_db_controller.get_all_items_exclude_hmbr(
        zid=zid, item_name=item, limit=limit, offset=offset
    )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No items found"),
        )
    return items