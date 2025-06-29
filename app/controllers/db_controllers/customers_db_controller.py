from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from models.customers_model import Cacus
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_normal_user
from schemas.customers_schema import CustomersSchema, CustomerOfferSchema
from typing import List
from fastapi import Depends, HTTPException, status
from logs import setup_logger

logger = setup_logger()

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
 
        try:
            user_id = employee_id
            
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
                    Cacus.xtitle.label("xtitle"),
                    Cacus.xfax.label("xfax"),
                    Cacus.xcreditr.label("xcreditr"),
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
            customers_records = result.fetchall()

            # Check if we found any customers before processing
            if not customers_records:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No customers found for employee ID: {user_id}"
                )            # Convert query results to list of CustomersSchema instances
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
                    xsp=customer.xsp,
                    xsp1=customer.xsp1,
                    xsp2=customer.xsp2,
                    xsp3=customer.xsp3,
                    # Split the xtitle at hyphen and take first part
                    xtitle=customer.xtitle.split('-')[0] if customer.xtitle else None,
                    xfax=customer.xfax, 
                    xcreditr=customer.xcreditr
                )
                for customer in customers_records
            ]

            return customers

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting customers for employee {employee_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customer information"
            )
        
    async def get_all_customers_sync(
        self, employee_id: str, limit: int, offset: int, current_user: UserRegistrationSchema = Depends(get_current_normal_user),
    ) -> List[CustomersSchema]:
        """Get all customers across all businesses for a specific employee ID."""
        if self.db is None:
            raise Exception("Database session not initialized.")
            
        try:
            user_id = employee_id
            
            # Construct the async query without zid filter
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
                    Cacus.xtitle.label("xtitle"),
                    Cacus.xfax.label("xfax"),
                    Cacus.xcreditr.label("xcreditr"),
                )
                .filter(
                    or_(
                        Cacus.xsp == user_id,
                        Cacus.xsp1 == user_id,
                        Cacus.xsp2 == user_id,
                        Cacus.xsp3 == user_id
                    )
                )
                .order_by(Cacus.xcus)
                .limit(limit)
                .offset(offset)
            )

            # Execute the query asynchronously
            result = await self.db.execute(stmt)
            customers_records = result.fetchall()

            # Check if we found any customers before processing
            if not customers_records:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No customers found for employee ID: {user_id}"
                )

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
                    xsp=customer.xsp,
                    xsp1=customer.xsp1,
                    xsp2=customer.xsp2,
                    xsp3=customer.xsp3,
                    # Split the xtitle at hyphen and take first part
                    xtitle=customer.xtitle.split('-')[0] if customer.xtitle else None,
                    xfax=customer.xfax, 
                    xcreditr=customer.xcreditr
                )
                for customer in customers_records
            ]

            return customers
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting synchronized customers for employee {employee_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customer information"
            )

    async def get_salesman_by_area(self, zid: int, area: str):
        """Get salesman information for a specific area."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Query to get first matching record
            result = await self.db.execute(
                select(
                    Cacus.xsp,
                    Cacus.xsp1,
                    Cacus.xsp2,
                    Cacus.xsp3
                ).filter(
                    Cacus.zid == zid,
                    Cacus.xcity.ilike(f"%{area}%")
                ).limit(1)
            )
            
            salesman = result.first()
            if not salesman:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No salesman found for area: {area} in zid: {zid}"
                )

            # Convert result to dictionary with proper field names
            return {
                "xsp": salesman[0],
                "xsp1": salesman[1],
                "xsp2": salesman[2],
                "xsp3": salesman[3]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting salesman info for area {area}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving salesman information"
            )

    async def update_salesman_by_area(self, zid: int, area: str, xsp: str = None, xsp1: str = None, xsp2: str = None, xsp3: str = None):
        """Update salesman assignments for customers in a specific area."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Build update values excluding None values
            update_values = {}
            if xsp is not None:
                update_values["xsp"] = xsp
            if xsp1 is not None:
                update_values["xsp1"] = xsp1
            if xsp2 is not None:
                update_values["xsp2"] = xsp2
            if xsp3 is not None:
                update_values["xsp3"] = xsp3

            if not update_values:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No salesman values provided for update"
                )

            # Execute update query
            result = await self.db.execute(
                Cacus.__table__.update()
                .where(
                    and_(
                        Cacus.zid == zid,
                        Cacus.xcity.ilike(f"%{area}%")
                    )
                )
                .values(**update_values)
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No customers found in area: {area} for zid: {zid}"
                )

            await self.db.commit()
            return {
                "message": f"Successfully updated salesman assignments for area: {area}",
                "updated_count": result.rowcount
            }
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating salesman assignments for area {area}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating salesman assignments"
            )

    async def get_areas_by_zid(self, zid: int, user_id: str = None):
        """Get distinct areas for a business, optionally filtered by salesman ID."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Build query based on whether user_id is provided
            query = select(Cacus.xcity).distinct().filter(Cacus.zid == zid)
            
            if user_id:
                query = query.filter(
                    or_(
                        Cacus.xsp == user_id,
                        Cacus.xsp1 == user_id,
                        Cacus.xsp2 == user_id,
                        Cacus.xsp3 == user_id
                    )
                )
            
            result = await self.db.execute(query)
            areas = [row[0] for row in result.fetchall() if row[0]]  # Filter out None values
            
            if not areas:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No areas found for zid: {zid}" + (f" and user_id: {user_id}" if user_id else "")
                )

            return {"areas": areas}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting areas for zid {zid}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving areas"
            )

    async def create_offer(self, request: CustomerOfferSchema, current_user: UserRegistrationSchema):
        """Create/Update offer for customers in a specific segment and zid."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            segment_value = request.xtitle.value
            result = await self.db.execute(
                Cacus.__table__.update()
                .where(
                    (Cacus.zid == request.zid) &
                    (Cacus.xtitle.ilike(f"%{segment_value}%"))
                )
                .values(
                    xcreditr=request.xcreditr,
                    xmonper=request.xmonper,
                    xmondiscper=request.xmondiscper,
                    xisgotmon=request.xisgotmon,
                    xisgotdefault=request.xisgotdefault
                )
            )   

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No customers found in zid {request.zid} and segment containing: {request.xtitle}"
                )

            await self.db.commit()
            return {
                "message": f"Successfully updated offers for all customers in zid {request.zid} and segment containing: {request.xtitle}",
                "updated_count": result.rowcount,
                "offer": request.xcreditr
            }
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating offers for zid {request.zid} segment {request.xtitle}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating customer offers"
            )
    # is customer got monitoring offer

    async def is_got_monitoring_offer(self, zid: int, xcus: str):
        """Atomically check & set xisgotmon to 'true' for a customer."""
        if self.db is None:
            raise Exception("Database session not initialized.")

        try:
            # Use savepoint to avoid "transaction already begun" error
            async with self.db.begin_nested():
                query = select(Cacus).filter(
                    Cacus.zid == zid,
                    Cacus.xcus == xcus
                ).with_for_update()

                result = await self.db.execute(query)
                customer = result.scalar_one_or_none()

                if not customer:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Customer not found"
                    )

                if customer.xisgotmon == 'true':
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Monitoring offer already given"
                    )

                customer.xisgotmon = 'true'

            await self.db.commit()
            await self.db.refresh(customer)

            return {
                "message": "Monitoring offer successfully given",
                "has_monitoring_offer": True
            }

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error checking/setting monitoring offer for customer {xcus}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking/setting monitoring offer"
            )
        
    # is customer got default offer
    async def is_got_default_offer(self, zid: int, xcus: str):
        """Atomically check & set xisgotdefault to 'true' for a customer."""
        if self.db is None:
            raise Exception("Database session not initialized.")

        try:
            # Use savepoint to allow nested transaction behavior
            async with self.db.begin_nested():
                query = select(Cacus).filter(
                    Cacus.zid == zid,
                    Cacus.xcus == xcus
                ).with_for_update()

                result = await self.db.execute(query)
                customer = result.scalar_one_or_none()

                if not customer:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Customer not found"
                    )

                if customer.xisgotdefault == 'true':
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Default offer already given"
                    )

                customer.xisgotdefault = 'true'

            # Commit outer transaction
            await self.db.commit()
            await self.db.refresh(customer)

            return {
                "message": "Default offer successfully given",
                "has_default_offer": True
            }

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error checking/setting default offer for customer {xcus}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error checking/setting default offer"
            )