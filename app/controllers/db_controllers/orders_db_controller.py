from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.orders_model import Opmob
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from utils.orders_utils import format_invoice_number, generate_random_number

class OrderDBController:
    """Controller for handling order-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _create_order_item(
        self, 
        zid: int,
        invoiceno: str,
        invoicesl: str,
        order_data: OpmobSchema,
        item_data: dict,
        current_user: UserRegistrationSchema
    ) -> Opmob:
        current_time = datetime.now()
        
        return Opmob(
            zid=zid,
            ztime=current_time,
            zutime=current_time,
            invoiceno=f"{current_user.terminal}-{invoiceno}",
            invoicesl=int(invoicesl),
            username=current_user.user_name,
            xemp=current_user.user_id,
            xcus=order_data.xcus,
            xcusname=order_data.xcusname,
            xcusadd=order_data.xcusadd,
            xitem=item_data.xitem,
            xdesc=item_data.xdesc,
            xqty=item_data.xqty,
            xprice=item_data.xprice,
            xroword=item_data.xroword,
            xterminal=current_user.terminal,
            xdate=current_time,
            xsl=str(uuid4()),
            xlat=item_data.xlat,
            xlong=item_data.xlong,
            xlinetotal=item_data.xlinetotal,
        )

    async def create_order(
        self, 
        zid: int, 
        order_data: OpmobSchema, 
        current_user: UserRegistrationSchema
    ) -> List[Opmob]:
        """Create a new order with multiple items."""
        # Generate invoice numbers
        invoicesl = generate_random_number(12)
        invoiceno = format_invoice_number(invoicesl)
        
        # Create order items
        created_items = []
        created_xsl_values = []  # Store XSL values for later retrieval
        
        for item in order_data.items:
            order_item = await self._create_order_item(
                zid=zid,
                invoiceno=invoiceno,
                invoicesl=invoicesl,
                order_data=order_data,
                item_data=item,
                current_user=current_user
            )
            self.db.add(order_item)
            created_items.append(order_item)
            created_xsl_values.append(order_item.xsl)  # Remember XSL values

        # Commit changes
        await self.db.commit()
        
        # Fetch the created items with fresh data by querying them separately
        # instead of calling refresh which can cause transaction issues
        result_items = []
        for xsl in created_xsl_values:
            # Execute a select query to get the fresh item
            stmt = select(Opmob).where(Opmob.xsl == xsl)
            result = await self.db.execute(stmt)
            fresh_item = result.scalar_one_or_none()
            if fresh_item:
                result_items.append(fresh_item)
            
        return result_items

    async def create_bulk_order(
        self, 
        zid: int, 
        orders_data: List[OpmobSchema], 
        current_user: UserRegistrationSchema
    ) -> List[Opmob]:
        """Create multiple orders in bulk."""
        all_created_items = []
        
        for order_data in orders_data:
            created_items = await self.create_order(zid, order_data, current_user)
            all_created_items.extend(created_items)
            
        return all_created_items
