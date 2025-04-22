from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from datetime import date
from schemas.customer_balance_schema import CustomerBalanceRequest, CustomerBalanceResponse
from controllers.db_controllers.customer_balance_controller import CustomerBalanceController
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_normal_user
from logs import setup_logger

logger = setup_logger()

router = APIRouter(
    prefix="/customer-balance",
    tags=["Customer Balance"]
)

@router.post("/", response_model=CustomerBalanceResponse)
async def get_customer_balance(
    request: CustomerBalanceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user)
):
    try:
        # Initialize the controller
        controller = CustomerBalanceController(db)
        
        # Set end date to today if not provided
        to_date = request.to_date or date.today()
        
        # Get customer ledger data with user validation
        opening_balance, ledger_entries = await controller.get_customer_ledger(
            zid=request.zid,
            customer_id=request.customer,
            start_date=request.frm_date,
            end_date=to_date,
            current_user=current_user
        )
        
        # Get closing balance (last running balance)
        closing_balance = ledger_entries[-1].running_balance if ledger_entries else opening_balance
        
        # Create response
        response = CustomerBalanceResponse(
            customer_id=request.customer,
            from_date=request.frm_date,
            to_date=to_date,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            ledger_entries=ledger_entries,
            total_entries=len(ledger_entries)
        )
        
        # Log successful request
        logger.info(f"Customer balance retrieved successfully by user {current_user.username} for customer {request.customer} in business {request.zid}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer balance for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving customer balance: {str(e)}"
        )
