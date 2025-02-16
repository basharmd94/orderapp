from sqlalchemy.orm import Session
from models.items_model import Caitem, Imtrn, Opspprc
from controllers.db_controllers.database_controller import DatabaseController
from schemas.items_schema import ItemsBaseSchema, ItemsSchema
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.functions import coalesce
from typing import Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

 
class ItemsDBController:
    """Controller for handling item-related database operations."""

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db  # Use the session passed in from the route handler

    async def get_all_items(
        self, zid: int, item_name: str, limit: int, offset: int
    ) -> List[ItemsSchema]:
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Define the CTE for transaction summary
        transaction_summary_query = (
            select(Imtrn.xitem, func.sum(Imtrn.xqty * Imtrn.xsign).label("stock"))
            .filter(Imtrn.zid == zid)
            .group_by(Imtrn.xitem)
        )

        transaction_summary = transaction_summary_query.cte("transaction_summary")
        query = (
            select(
                Caitem.zid.label("zid"),
                Caitem.xitem.label("item_id"),
                Caitem.xdesc.label("item_name"),
                Caitem.xgitem.label("item_group"),
                Caitem.xstdprice.label("std_price"),
                Caitem.xunitstk.label("stock_unit"),
                transaction_summary.c.stock,
                func.coalesce(func.min(Opspprc.xqty), 0).label("min_disc_qty"),
                func.coalesce(func.min(Opspprc.xdisc), 0).label("disc_amt"),
            )
            .join(transaction_summary, Caitem.xitem == transaction_summary.c.xitem)
            .outerjoin(
                Opspprc, and_(Caitem.xitem == Opspprc.xpricecat, Opspprc.zid == zid)
            )
            .filter(
                Caitem.zid == zid,
                transaction_summary.c.stock > 0,
                or_(
                    Caitem.xdesc.ilike(f"%{item_name}%"),  # Dynamic item_name
                    Caitem.xdesc.ilike(f"%{item_name}%"),  # Dynamic item_name
                    Caitem.xitem.ilike(f"%{item_name}%"),  # Dynamic item_name
                    Caitem.xgitem.ilike(f"%{item_name}%"),  # Dynamic item_name
                ),
                Caitem.xgitem.notin_(
                    [
                        "Stationary",
                        "Administrative Item",
                        "Advertisement Item Marketing",
                        "Cleaning Item",
                        "Maintenance Item",
                        "Marketing & Advertisement",
                        "Packaging Item",
                        "Zepto Raw Metrial",
                        "RAW Material PL",
                        "RAW Material CH"
                    ]
                ),
            )
            .group_by(
                Caitem.zid,
                Caitem.xitem,
                Caitem.xdesc,
                Caitem.xgitem,
                Caitem.xstdprice,
                Caitem.xunitstk,
                transaction_summary.c.stock,
            )
            .order_by(Caitem.xitem)
            .limit(limit)  # Dynamic limit
            .offset(offset)  # Dynamic offset
        )
        # Execute the main query asynchronously
        result = await self.db.execute(query)

        # Convert the query results to a list of ItemsSchema instances
        items = [
            ItemsSchema(
                zid=item.zid,
                item_id=item.item_id,
                item_name=item.item_name,
                item_group=item.item_group,
                std_price=item.std_price,
                stock=item.stock,
                min_disc_qty=item.min_disc_qty,
                disc_amt=item.disc_amt,
            )
            for item in result.fetchall()  # Use fetchall to get the full result
        ]
        return items

    async def get_all_items_exclude_hmbr(
        self, zid: int, item_name: str, limit: int, offset: int
    ) -> List[ItemsBaseSchema]:
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Define the CTE for transaction summary
        transaction_summary_query = (
            select(Imtrn.xitem, func.sum(Imtrn.xqty * Imtrn.xsign).label("stock"))
            .filter(Imtrn.zid == zid)
            .group_by(Imtrn.xitem)
        )

        transaction_summary = transaction_summary_query.cte("transaction_summary")

        # The main query using the CTE
        query = (
            select(
                Caitem.zid.label("zid"),
                Caitem.xitem.label("item_id"),
                Caitem.xdesc.label("item_name"),
                Caitem.xgitem.label("item_group"),
                Caitem.xstdprice.label("std_price"),
                Caitem.xunitstk.label("stock_unit"),
                transaction_summary.c.stock,
            )
            .join(transaction_summary, Caitem.xitem == transaction_summary.c.xitem)
            .outerjoin(
                Opspprc, and_(Caitem.xitem == Opspprc.xpricecat, Opspprc.zid == zid)
            )
            .filter(
                Caitem.zid == zid,
                transaction_summary.c.stock > 0,
                or_(

                    Caitem.xdesc.ilike(f"%{item_name}%"),  # Dynamic item_name
                    Caitem.xitem.ilike(f"%{item_name}%"),  # Dynamic item_name
                    Caitem.xgitem.ilike(f"%{item_name}%"),  # Dynamic item_name
                ),
                Caitem.xgitem.notin_(
                    [
                        "Stationary",
                        "Administrative Item",
                        "Advertisement Item Marketing",
                        "Cleaning Item",
                        "Maintenance Item",
                        "Marketing & Advertisement",
                        "Packaging Item",
                        "Zepto Raw Metrial",
                        "RAW Material PL",
                        "RAW Material CH"
                    ]
                ),
            )
            .group_by(
                Caitem.zid,
                Caitem.xitem,
                Caitem.xdesc,
                Caitem.xgitem,
                Caitem.xstdprice,
                Caitem.xunitstk,
                transaction_summary.c.stock,
            )
            .order_by(Caitem.xitem)
            .limit(limit)
            .offset(offset)
        )

        # Execute the main query asynchronously
        result = await self.db.execute(query)

        # Convert the query results to a list of ItemsBaseSchema instances
        items = [
            ItemsBaseSchema(
                zid=item.zid,
                item_id=item.item_id,
                item_name=item.item_name,
                item_group=item.item_group,
                std_price=item.std_price,
                stock=item.stock,
            )
            for item in result.fetchall()  # Use fetchall to get the full result
        ]
        return items
