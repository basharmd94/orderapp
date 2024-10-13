from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from models.customers_model import Cacus
from schemas.customers_schema import CustomersSchema
from typing import List
# from controllers.db_controllers.database_controller import DatabaseController


class CustomersDBController:
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db  # Use the session passed in from the route handler

    async def get_all_customers(
        self, zid: int, customer: str, limit: int, offset: int
    ) -> List[CustomersSchema]:
        """Get all customers based on filter criteria."""

        # Ensure the database session is initialized
        if self.db is None:
            raise Exception("Database session not initialized.")

        async with self.db.begin():  # Open a transaction with the session
            try:
                # Construct the async query
                stmt = (
                    select(Cacus)
                    .filter(
                        Cacus.zid == zid,
                        or_(
                            Cacus.xcus.ilike(f"%{customer}%"),
                            Cacus.xorg.ilike(f"%{customer}%"),
                            Cacus.xcity.ilike(f"%{customer}%"),
                            Cacus.xtaxnum.ilike(f"%{customer}%"),
                            Cacus.xmobile.ilike(f"%{customer}%"),
                        ),
                    )
                    .order_by(Cacus.xcus)
                    .limit(limit)
                    .offset(offset)
                )

                # Execute the query asynchronously
                result = await self.db.execute(stmt)
                customers_records = result.scalars().all()

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
                        xsp=[
                            x
                            for x in [customer.xsp1, customer.xsp2, customer.xsp3]
                            if x
                        ],
                    )
                    for customer in customers_records
                ]

                return customers

            except Exception as e:
                # Rollback the session in case of an error
                await self.db.rollback()
                raise e
