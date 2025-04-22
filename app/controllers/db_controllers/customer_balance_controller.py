from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, func, select
from datetime import date, datetime
from models.finance import GLHeader, GLDetail
from typing import Optional, Tuple, List
from schemas.customer_balance_schema import LedgerEntry
from fastapi import HTTPException, status
from logs import setup_logger

logger = setup_logger()

class CustomerBalanceController:
    def __init__(self, db: AsyncSession):
        self.db = db

    def get_project_by_zid(self, zid: int) -> str:
        """Get project name based on business ID."""
        projects = {
            100000: "GI Corporation",
            100001: "GULSHAN TRADING",
            100005: "Zepto Chemicals"
        }
        return projects.get(zid)

    async def validate_user_access(self, zid: int, customer_id: str, current_user) -> None:
        """Validate if user has access to the customer data."""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        project = self.get_project_by_zid(zid)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid business ID: {zid}"
            )

        # Log the access attempt
        logger.info(f"User {current_user.username} ({current_user.username}) accessing customer balance for {customer_id} in {project}")

        # For additional validation similar to customers_db_controller if needed
        # Add any specific validation rules here

    async def get_payment_data(self, zid: int, customer_id: str, start_date: date, end_date: date) -> List[dict]:
        try:
            h = aliased(GLHeader)
            g = aliased(GLDetail)
            
            query = select(
                h.xdate.label('last_pay_date'),
                g.xsub.label('xcus'),
                g.xprime.label('last_rec_amt'),
                h.xvoucher.label('xvoucher')
            ).select_from(h).join(
                g, and_(h.xvoucher == g.xvoucher, h.zid == g.zid)
            ).filter(
                h.zid == zid,
                g.zid == zid,
                g.xsub == customer_id,
                h.xdate.between(start_date, end_date),
                or_(
                    h.xvoucher.like('%RCT-%'),
                    h.xvoucher.like('JV--%'),
                    h.xvoucher.like('RCT-%'),
                    h.xvoucher.like('CRCT%'),
                    h.xvoucher.like('STJV%'),
                    h.xvoucher.like('BRCT%')
                )
            ).order_by(g.xsub, h.xdate)
            
            result = await self.db.execute(query)
            results = result.fetchall()
            
            return [
                {
                    'last_pay_date': row.last_pay_date,
                    'xcus': row.xcus,
                    'last_rec_amt': float(row.last_rec_amt) if row.last_rec_amt is not None else 0.0,
                    'xvoucher': row.xvoucher
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"Error getting payment data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving payment data: {str(e)}"
            )

    async def get_order_data(self, zid: int, customer_id: str, start_date: date, end_date: date) -> List[dict]:
        try:
            h = aliased(GLHeader)
            g = aliased(GLDetail)
            
            query = select(
                h.xdate.label('last_order_date'),
                g.xsub.label('xcus'),
                g.xprime.label('last_order_amt'),
                h.xvoucher.label('xvoucher')
            ).select_from(h).join(
                g, and_(h.xvoucher == g.xvoucher, h.zid == g.zid)
            ).filter(
                h.zid == zid,
                g.zid == zid,
                g.xsub == customer_id,
                h.xdate.between(start_date, end_date),
                h.xvoucher.like('%INOP%')
            ).order_by(g.xsub, h.xdate)
            
            result = await self.db.execute(query)
            results = result.fetchall()
            
            return [
                {
                    'last_order_date': row.last_order_date,
                    'xcus': row.xcus,
                    'last_order_amt': float(row.last_order_amt) if row.last_order_amt is not None else 0.0,
                    'xvoucher': row.xvoucher
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"Error getting order data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving order data: {str(e)}"
            )

    async def get_closing_balance(self, zid: int, customer_id: str, closing_date: date) -> float:
        try:
            g = aliased(GLDetail)
            h = aliased(GLHeader)
            
            project = self.get_project_by_zid(zid)
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid business ID: {zid}"
                )
            
            query = select(
                func.sum(g.xprime).label('closing_balance')
            ).select_from(g).join(
                h, and_(g.xvoucher == h.xvoucher, g.zid == h.zid)
            ).filter(
                h.zid == zid,
                g.zid == zid,
                g.xsub == customer_id,
                g.xproj == project,
                ~g.xvoucher.like('%OB%'),
                h.xdate < closing_date
            )
            
            result = await self.db.execute(query)
            scalar_result = result.scalar()
            return float(scalar_result) if scalar_result is not None else 0.0
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting closing balance: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving closing balance: {str(e)}"
            )

    async def get_customer_ledger(self, zid: int, customer_id: str, start_date: date, end_date: date, current_user) -> Tuple[float, List[LedgerEntry]]:
        try:
            # Validate user access first
            await self.validate_user_access(zid, customer_id, current_user)
            
            # Get opening balance
            opening_balance = await self.get_closing_balance(zid, customer_id, start_date)
            
            # Get payments and orders
            payments = await self.get_payment_data(zid, customer_id, start_date, end_date)
            orders = await self.get_order_data(zid, customer_id, start_date, end_date)
            
            # Process payments
            ledger_entries = []
            running_balance = opening_balance

            # Add opening balance entry
            ledger_entries.append(LedgerEntry(
                transaction_date=start_date,
                entry_type="OPENING",
                amount=0.0,
                voucher="N/A",
                running_balance=opening_balance
            ))

            # Process all transactions
            all_transactions = []
            
            for payment in payments:
                all_transactions.append({
                    'date': payment['last_pay_date'],
                    'type': 'PAYMENT',
                    'amount': payment['last_rec_amt'],
                    'voucher': payment['xvoucher']
                })
                
            for order in orders:
                all_transactions.append({
                    'date': order['last_order_date'],
                    'type': 'ORDER',
                    'amount': order['last_order_amt'],
                    'voucher': order['xvoucher']
                })
                
            # Sort transactions by date
            all_transactions.sort(key=lambda x: x['date'])
            
            # Create ledger entries
            for trans in all_transactions:
                running_balance += trans['amount']
                ledger_entries.append(LedgerEntry(
                    transaction_date=trans['date'],
                    entry_type=trans['type'],
                    amount=trans['amount'],
                    voucher=trans['voucher'],
                    running_balance=running_balance
                ))
                
            return opening_balance, ledger_entries
        except Exception as e:
            logger.error(f"Error getting customer ledger: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving customer ledger: {str(e)}"
            )
