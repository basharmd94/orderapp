from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from models.orders_model import Opmob
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from utils.orders_utils import format_invoice_number, generate_random_number
from schemas.order_summary_schema import OrderSummaryResponse, OrderSummaryListResponse

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
            username=current_user.username,
            xemp=current_user.employeeCode,
            xcus=order_data.xcus,
            xcusname=order_data.xcusname,
            xcusadd=order_data.xcusadd,
            xitem=item_data.xitem,
            xdesc=item_data.xdesc,
            xqty=item_data.xqty,
            xprice=item_data.xprice,
            xstatusord = "New",
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
    
    async def get_orders_by_status(
        self, 
        status: str,
        username: str,
        zid: int = None,
        limit: int = 10
    ) -> OrderSummaryListResponse:
        """Get orders with a specific status for the current user."""
        try:
            # Build the SQL query with string aggregation
            query = text("""
                SELECT 
                    zid,
                    invoiceno, 
                    xcus, 
                    xcusname, 
                    STRING_AGG(xitem || ' - ' || xdesc, ', ') AS items,
                    SUM(xqty) AS total_qty, 
                    SUM(xprice) AS total_price, 
                    SUM(xlinetotal) AS total_linetotal,
                    xstatusord
                FROM 
                    opmob
                WHERE 
                    username = :username 
                    AND xstatusord = :status
                    """ + (f" AND zid = :zid" if zid else "") + """
                GROUP BY 
                    zid,
                    invoiceno, 
                    xcus, 
                    xcusname, 
                    xstatusord
                ORDER BY 
                    invoiceno
                LIMIT :limit
            """)
            
            # Prepare parameters
            params = {
                "username": username,
                "status": status,
                "limit": limit
            }
            
            if zid:
                params["zid"] = zid
                
            # Execute the query
            result = await self.db.execute(query, params)
            orders = result.fetchall()
            
            # Convert to OrderSummaryResponse objects
            order_summaries = [
                OrderSummaryResponse(
                    zid=order.zid,
                    invoiceno=order.invoiceno,
                    xcus=order.xcus,
                    xcusname=order.xcusname,
                    items=order.items,
                    total_qty=order.total_qty,
                    total_price=float(order.total_price),
                    total_linetotal=float(order.total_linetotal),
                    xstatusord=order.xstatusord
                )
                for order in orders
            ]
            
            return OrderSummaryListResponse(
                orders=order_summaries,
                count=len(order_summaries),
                status=status
            )
            
        except Exception as e:
            # Re-raise the exception with additional context
            raise Exception(f"Error fetching {status} orders: {str(e)}")
            
    async def get_pending_orders(self, username: str, zid: int = None, limit: int = 10) -> OrderSummaryListResponse:
        """Get pending (new) orders for the current user."""
        return await self.get_orders_by_status("New", username, zid, limit)
        
    async def get_confirmed_orders(self, username: str, zid: int = None, limit: int = 10) -> OrderSummaryListResponse:
        """Get confirmed orders for the current user."""
        return await self.get_orders_by_status("Order Created", username, zid, limit)
        
    async def get_cancelled_orders(self, username: str, zid: int = None, limit: int = 10) -> OrderSummaryListResponse:
        """Get cancelled orders for the current user."""
        return await self.get_orders_by_status("Not enough stock to create Order", username, zid, limit)
