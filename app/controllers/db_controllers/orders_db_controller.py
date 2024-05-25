from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.users_model import ApiUsers
from controllers.db_controllers.database_controller import DatabaseController
from utils.orders_utils import format_invoice_number, generate_random_number
from schemas.orders_schema import OpmobSchema
from schemas.user_schema import UserRegistrationSchema
from models.orders_model import Opmob
import logging
from uuid import uuid4

class OrderDBController(DatabaseController):

    def create_order(
        self, zid:int, order_data: OpmobSchema, current_user: UserRegistrationSchema
    ):
        logger = logging.getLogger("OrderDBController")

        # Generate random 15-digit number for invoicesl
        invoicesl = generate_random_number(12)

        # Format invoicesl and create invoiceno
        invoiceno = format_invoice_number(invoicesl)

        # Get terminal from current user
        terminal = current_user.terminal

        # # Log the received ztime and zutime values
        # logger.info(f"Received ztime: {order_data.ztime}")
        # logger.info(f"Received zutime: {order_data.zutime}")

        # try:
        #     # Parse ztime and zutime to datetime objects
        #     ztime = datetime.strptime(order_data.ztime, '%Y-%m-%dT%H:%M:%S')
        #     zutime = datetime.strptime(order_data.zutime, '%Y-%m-%dT%H:%M:%S')
        # except ValueError as e:
        #     logger.error(f"Error parsing datetime: {e}")
        #     raise ValueError("Invalid datetime format. Expected format: '%Y-%m-%dT%H:%M:%S'")

        # Create string date for xdate
        xdate = datetime.now().strftime("%Y-%m-%d")

        created_items = []
        for item_data in order_data.items:
            db_item = Opmob(
                zid=zid,
                invoiceno=f"{terminal}-{invoiceno}",
                invoicesl=invoicesl,
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
                xterminal=terminal,
                xdate=xdate,  # Use the created string date
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

        self.db.commit()

        for item in created_items:
            self.db.refresh(item)

        return created_items
