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
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = setup_logger()


@router.get(
    "/all/{zid}", response_model=Union[List[ItemsSchema], List[ItemsBaseSchema]]
)
async def get_all_items(
    request: Request,
    zid: int,
    item: Annotated[str, Query( description="Put Items ID or Items Name")],
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),  # Inject database session
    current_user: UserRegistrationSchema = Depends(get_current_normal_user),
):
    logger.info(f"get all items endpoint called: {request.url.path}")

    # Pass the db session to ItemsDBController
    items_db_controller = ItemsDBController(db)

    # if zid in [100000, 100001]:
    items = await items_db_controller.get_all_items(
        zid=zid, item_name=item, limit=limit, offset=offset
    )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No items found"),
        )
    return items

    # items = await items_db_controller.get_all_items_exclude_hmbr(
    #     zid=zid, item_name=item, limit=limit, offset=offset
    # )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_details("No items found"),
        )
    return items

@router.get(
    "/items_without_auth",
    response_model=Union[List[ItemsSchema], List[ItemsBaseSchema]],
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
    items_db_controller = ItemsDBController()

    await items_db_controller.connect()
    try:
        if zid in [100000, 100001]:
            items = await items_db_controller.get_all_items(
                zid=zid, item_name=item, limit=limit, offset=offset
            )
        else:
            items = await items_db_controller.get_all_items_exclude_hmbr(
                zid=zid, item_name=item, limit=limit, offset=offset
            )

        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_details("No items found"),
            )

        return items  # Ensure that items are returned regardless of the condition

    finally:
        await items_db_controller.close()



order = {
  "xcus": "string",
  "items": [
    {
      "xitem": "string",
      "xdesc": "string",
      "xqty": 0,
      "xprice": 0,
      "xroword": 0,
      "xdate": "string",
      "xsl": "string",
      "xlat": 0,
      "xlong": 0,
      "xlinetotal": 0
    }
  ]
}