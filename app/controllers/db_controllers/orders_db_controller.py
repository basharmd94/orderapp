from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.users_model import ApiUsers
from controllers.db_controllers.database_controller import DatabaseController
from sqlalchemy.ext.asyncio import AsyncSession
from utils.orders_utils import format_invoice_number, generate_random_number
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from models.orders_model import Opmob
import logging
from uuid import uuid4

class OrderDBController:
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db  # Use the session passed in from the route handler


    async def create_order(
        self, zid:int, order_data: OpmobSchema, current_user: UserRegistrationSchema
    ):

        # Generate random 15-digit number for invoicesl
        invoicesl = generate_random_number(12)
        print (current_user.terminal)

        # Format invoicesl and create invoiceno
        invoiceno = format_invoice_number(invoicesl)

        # Create string date for xdate
        xdate = datetime.now().strftime("%Y-%m-%d")
 
        created_items = []
        for item_data in order_data.items:
            db_item = Opmob( 
                zid=zid,
                ztime=datetime.now(),
                zutime = datetime.now(),
                invoiceno=f"{current_user.terminal}-{invoiceno}",
                invoicesl= int(invoicesl),
                username=current_user.user_name,
                xemp=current_user.user_id,
                xcus=order_data.xcus,
                xcusname=order_data.xcusname,
                xcusadd=order_data.xcusadd,
                xitem=item_data.xitem,
                xdesc=item_data.xdesc,
                xqty=item_data.xqty,
                xprice=item_data.xprice,
                # xstatusord=item_data.xstatusord,
                # xordernum=item_data.xordernum,
                xroword=item_data.xroword,
                xterminal=current_user.terminal,
                xdate= datetime.now(),  # Use the created string date
                xsl=str(uuid4()),
                xlat=item_data.xlat,
                xlong=item_data.xlong,
                xlinetotal=item_data.xlinetotal,
                # xtra1=item_data.xtra1,
                # xtra2=item_data.xtra2,
                # xtra3=item_data.xtra3,
                # xtra4=item_data.xtra4,
                # xtra5=item_data.xtra5,
            )
            self.db.add(db_item)
            created_items.append(db_item)

        await self.db.commit()

        for item in created_items:
            await self.db.refresh(item)

        return created_items
