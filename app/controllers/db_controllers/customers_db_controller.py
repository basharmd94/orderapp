from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.customers_model import Cacus
from schemas.customers_schema import CustomersSchema
from typing import List
from database import get_db  # Import the database session provider

class DatabaseController:
    def __init__(self):
        self.db = next(get_db())


class CustomersDBController(DatabaseController):
    """Controller for handling customer-related database operations."""

    @classmethod
    def get_all_customers(cls, zid: int, customer: str, limit: int, offset: int) -> List[CustomersSchema]:
        with next(get_db()) as session:  # Ensure session is managed within the method
            try:
                # Query to fetch customer data
                query = session.query(Cacus).filter(
                    Cacus.zid == zid,
                    or_(
                        Cacus.xcus.ilike(f"%{customer}%"),
                        Cacus.xorg.ilike(f"%{customer}%"),
                        Cacus.xcity.ilike(f"%{customer}%"),
                        Cacus.xtaxnum.ilike(f"%{customer}%"),
                        Cacus.xmobile.ilike(f"%{customer}%"),
                    )
                ).order_by("xcus").limit(limit).offset(offset)

                # Convert the query results to list of CustomersSchema instances
                customers = []
                for customer in query.all():
                    xsp_list = [customer.xsp1, customer.xsp2, customer.xsp3]  # List of xsp1, xsp2, xsp3 values
                    xsp = [x for x in xsp_list if x]  # Remove None values
                    customer_data = CustomersSchema(
                        zid=customer.zid,
                        xcus=customer.xcus,
                        xorg=customer.xorg,
                        xadd1=customer.xadd1,
                        xcity=customer.xcity,
                        xstate=customer.xstate,
                        xmobile=customer.xmobile,
                        xtaxnum=customer.xtaxnum,
                        xsp=xsp,  # Assign the list of strings to xsp
                    )
                    customers.append(customer_data)
                return customers
            except Exception as e:
                session.rollback()
                raise e