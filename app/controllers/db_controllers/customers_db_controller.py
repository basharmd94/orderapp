from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from models.customers_model import Cacus
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_normal_user
from schemas.customers_schema import CustomersSchema
from typing import List
from fastapi import Depends

class CustomersDBController:
    """Controller for handling customer-related database operations."""

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db  # Use the session passed in from the route handler

    async def get_all_customers(
        self, zid: int, customer: str, employee_id:str, limit: int, offset: int,  current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    ) -> List[CustomersSchema]: 
        """Get all customers based on filter criteria."""
        if self.db is None:
            raise Exception("Database session not initialized.")

        # Extract user_id from current_user tuple
        user_id = employee_id  # Assuming user_id is in the format ('ID',)
        print (user_id, "HERE IS USER IDD" , current_user.user_name)
        # Construct the async query
        stmt = (
            select(
                Cacus.zid.label("zid"),
                Cacus.xcus.label("xcus"),
                Cacus.xorg.label("xorg"),
                Cacus.xadd1.label("xadd1"),
                Cacus.xcity.label("xcity"),
                Cacus.xstate.label("xstate"),
                Cacus.xmobile.label("xmobile"),
                Cacus.xtaxnum.label("xtaxnum"),
                Cacus.xsp.label("xsp"),
                Cacus.xsp1.label("xsp1"),
                Cacus.xsp2.label("xsp2"),
                Cacus.xsp3.label("xsp3"),
            )
            .filter(
                Cacus.zid == zid,
                or_(
                    Cacus.xcus.ilike(f"%{customer}%"),
                    Cacus.xorg.ilike(f"%{customer}%"),
                    Cacus.xcity.ilike(f"%{customer}%"),
                    Cacus.xtaxnum.ilike(f"%{customer}%"),
                    Cacus.xmobile.ilike(f"%{customer}%"),
                ),
                and_(
                    or_(
                        Cacus.xsp == user_id,
                        Cacus.xsp1 == user_id,
                        Cacus.xsp2 == user_id,
                        Cacus.xsp3 == user_id
                    )
                )
            )
            .order_by(Cacus.xcus)
            .limit(limit)
            .offset(offset)
        )

        # Execute the query asynchronously
        result = await self.db.execute(stmt)
        customers_records = result.fetchall()  # Fetch all the results

        # Convert query results to list of CustomersSchema instances
        customers = [
            CustomersSchema(
                zid=customer.zid,
                xcus=customer.xcus,
                xorg=customer.xorg,
                xadd1=customer.xadd1,
                xcity=customer.xcity,
                xstate=customer.xstate,
                xmobile=customer.xmobile,
                xtaxnum=customer.xtaxnum,
                xsp=[customer.xsp, customer.xsp1, customer.xsp2, customer.xsp3],
            )
            for customer in customers_records
        ]

        return customers
