from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.db_controllers.feedback_db_controller import FeedbackDBController
from schemas.feedback_schema import FeedbackCreate, FeedbackResponse, FeedbackQuery
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_normal_user
from logs import setup_logger
from typing import List

router = APIRouter(
    tags=["Feedback"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)

logger = setup_logger()

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedbackResponse
)
async def create_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user)
):
    """
    Create a new feedback entry.
    
    - **zid**: Business ID
    - **customer_id**: Customer ID associated with the feedback
    - **product_id**: Product ID associated with the feedback
    - **is_delivery_issue**: Whether there's a delivery issue (default: false)
    - **is_collection_issue**: Whether there's a collection issue (default: false)
    - **description**: Detailed feedback description (can be in Bangla)
    - **user_id**: User ID associated with the feedback (optional)
    """
    try:
        feedback_controller = FeedbackDBController(db)
        result = await feedback_controller.create_feedback(feedback, current_user.username)
        
        # Use the dictionary result directly with Pydantic model
        return FeedbackResponse(**result)
    except Exception as e:
        logger.error(f"Error creating feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feedback: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[FeedbackResponse]
)
async def get_feedbacks(
    zid: int = None,
    customer_id: str = None,
    product_id: str = None,
    is_delivery_issue: bool = None,
    is_collection_issue: bool = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: UserRegistrationSchema = Depends(get_current_normal_user)
):
    """
    Get feedback entries with optional filters.
    
    - **zid**: Filter by business ID
    - **customer_id**: Filter by customer ID
    - **product_id**: Filter by product ID
    - **is_delivery_issue**: Filter by delivery issue status
    - **is_collection_issue**: Filter by collection issue status
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Number of results to skip (default: 0)
    """
    try:
        query_params = FeedbackQuery(
            zid=zid,
            customer_id=customer_id,
            product_id=product_id,
            is_delivery_issue=is_delivery_issue,
            is_collection_issue=is_collection_issue,
            limit=limit,
            offset=offset
        )
        
        feedback_controller = FeedbackDBController(db)
        results = await feedback_controller.get_feedbacks(query_params)
        
        # Convert to response format
        return [FeedbackResponse(**result) for result in results]
    except Exception as e:
        logger.error(f"Error getting feedbacks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feedbacks: {str(e)}"
        )