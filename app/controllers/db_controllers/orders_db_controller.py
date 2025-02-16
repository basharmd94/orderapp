from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from models.orders_model import Opmob
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from utils.orders_utils import format_invoice_number, generate_random_number

class OrderDBController:
    """Controller for handling order-related database operations. hellow world"""

    
    def __init__(self, db: AsyncSession):
        """Initialize the controller with a database session.
        
        Args:
            db (AsyncSession): The database session to use for operations
        """
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
        """Create a single order item in the database.
        
        Args:
            zid (int): Zone ID
            invoiceno (str): Formatted invoice number
            invoicesl (str): Invoice serial number
            order_data (OpmobSchema): Order data containing customer information
            item_data (dict): Individual item data
            current_user (UserRegistrationSchema): Current user information
            
        Returns:
            Opmob: Created order item
        """
        current_time = datetime.now()
        
        return Opmob(
            zid=zid,
            ztime=current_time,
            zutime=current_time,
            invoiceno=f"{current_user.terminal}-{invoiceno}",
            invoicesl=int(invoicesl),  # Convert to int here for database
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
        """Create a new order with multiple items.
        
        Args:
            zid (int): Zone ID
            order_data (OpmobSchema): Order data containing customer and items information
            current_user (UserRegistrationSchema): Current user information
            
        Returns:
            List[Opmob]: List of created order items
        """
        # Generate invoice numbers - keep as string until database insertion
        invoicesl = generate_random_number(12)  # Returns string
        invoiceno = format_invoice_number(invoicesl)
        
        # Create order items
        created_items = []
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

        # Commit all changes at once
        await self.db.commit()
        
        # Refresh all items to get their updated state
        for item in created_items:
            await self.db.refresh(item)
            
        return created_items

    async def create_bulk_order(
        self, 
        zid: int, 
        orders_data: List[OpmobSchema], 
        current_user: UserRegistrationSchema
    ) -> List[Opmob]:
        """Create multiple orders in bulk.
        
        Args:
            zid (int): Zone ID
            orders_data (List[OpmobSchema]): List of orders to create
            current_user (UserRegistrationSchema): Current user information
            
        Returns:
            List[Opmob]: List of all created order items
        """
        all_created_items = []
        
        for order_data in orders_data:
            created_items = await self.create_order(zid, order_data, current_user)
            all_created_items.extend(created_items)
            
        return all_created_items
