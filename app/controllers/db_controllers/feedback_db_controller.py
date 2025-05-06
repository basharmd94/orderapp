from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from models.feedback_model import Feedback
from models.customers_model import Cacus
from models.items_model import Caitem
from schemas.feedback_schema import FeedbackCreate, FeedbackResponse, FeedbackQuery
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from logs import setup_logger

logger = setup_logger()

class FeedbackDBController:
    """Controller for handling feedback-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_feedback(self, feedback_data: FeedbackCreate, username: str) -> Dict[str, Any]:
        """Create a new feedback entry."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Verify customer exists
            customer_result = await self.db.execute(
                select(Cacus).filter(
                    and_(
                        Cacus.zid == feedback_data.zid,
                        Cacus.xcus == feedback_data.customer_id
                    )
                )
            )
            customer = customer_result.scalars().first()
            
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer {feedback_data.customer_id} not found in business {feedback_data.zid}"
                )
            
            # Verify product exists (only if product_id is provided)
            valid_product = False
            if feedback_data.product_id is not None:
                product_result = await self.db.execute(
                    select(Caitem).filter(
                        and_(
                            Caitem.zid == feedback_data.zid,
                            Caitem.xitem == feedback_data.product_id
                        )
                    )
                )
                product = product_result.scalars().first()
                
                if product:
                    valid_product = True
                else:
                    # Try numeric product ID if not found directly
                    try:
                        product_id_numeric = feedback_data.product_id
                        product_result = await self.db.execute(
                            select(Caitem).filter(
                                and_(
                                    Caitem.zid == feedback_data.zid,
                                    Caitem.xitem.like(f"%{product_id_numeric}")
                                )
                            )
                        )
                        product = product_result.scalars().first()
                        
                        if product:
                            # Use the actual product ID from database
                            feedback_data.product_id = product.xitem
                            valid_product = True
                        else:
                            # Product not found, set to None instead of raising an error
                            logger.warning(f"Product {feedback_data.product_id} not found, setting to None")
                            feedback_data.product_id = None
                    except (ValueError, TypeError):
                        # Product not found, set to None instead of raising an error
                        logger.warning(f"Product {feedback_data.product_id} not found, setting to None")
                        feedback_data.product_id = None
            
            # Create feedback object with base data
            new_feedback = Feedback(
                zid=feedback_data.zid,
                customer_id=feedback_data.customer_id,
                product_id=feedback_data.product_id,
                is_delivery_issue=feedback_data.is_delivery_issue,
                is_collection_issue=feedback_data.is_collection_issue,
                description=feedback_data.description,
                created_by=username,
                user_id=feedback_data.user_id
            )
            
            # Add to session and commit
            self.db.add(new_feedback)
            await self.db.commit()
            await self.db.refresh(new_feedback)
            
            # Return as dictionary
            return {
                "id": new_feedback.id,
                "zid": new_feedback.zid,
                "customer_id": new_feedback.customer_id,
                "product_id": new_feedback.product_id,
                "is_delivery_issue": new_feedback.is_delivery_issue,
                "is_collection_issue": new_feedback.is_collection_issue,
                "description": new_feedback.description,
                "translated_desc": new_feedback.translated_desc,
                "created_at": new_feedback.created_at,
                "updated_at": new_feedback.updated_at,
                "created_by": new_feedback.created_by,
                "user_id": new_feedback.user_id
            }
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating feedback: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating feedback: {str(e)}"
            )

    async def get_feedbacks(self, query_params: FeedbackQuery) -> List[Dict[str, Any]]:
        """Get feedback entries with applied filters."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Debug log query parameters
            logger.info(f"Feedback search parameters: {query_params}")
            
            # Start building the query
            query = select(Feedback)
            
            # Apply filters if provided
            if query_params.zid is not None:
                query = query.filter(Feedback.zid == query_params.zid)
                
            if query_params.customer_id is not None:
                query = query.filter(Feedback.customer_id == query_params.customer_id)
                
            if query_params.product_id is not None:
                query = query.filter(Feedback.product_id == query_params.product_id)
                
            if query_params.is_delivery_issue is not None:
                query = query.filter(Feedback.is_delivery_issue == query_params.is_delivery_issue)
                
            if query_params.is_collection_issue is not None:
                query = query.filter(Feedback.is_collection_issue == query_params.is_collection_issue)
                
            if query_params.created_by is not None:
                query = query.filter(Feedback.created_by == query_params.created_by)
                
            if query_params.start_date is not None and query_params.end_date is not None:
                query = query.filter(
                    and_(
                        Feedback.created_at >= query_params.start_date,
                        Feedback.created_at <= query_params.end_date
                    )
                )
            elif query_params.start_date is not None:
                query = query.filter(Feedback.created_at >= query_params.start_date)
            elif query_params.end_date is not None:
                query = query.filter(Feedback.created_at <= query_params.end_date)
            
            # Add ordering, limit and offset
            query = query.order_by(Feedback.created_at.desc())
            
            if query_params.limit is not None:
                query = query.limit(query_params.limit)
                
            if query_params.offset is not None:
                query = query.offset(query_params.offset)
            
            # Execute the query
            result = await self.db.execute(query)
            feedbacks = result.scalars().all()
            
            # Log the number of results
            logger.info(f"Found {len(feedbacks)} feedback entries matching the criteria")
            
            # Convert to response format
            response_feedbacks = []
            for feedback in feedbacks:
                response_feedbacks.append({
                    "id": feedback.id,
                    "zid": feedback.zid,
                    "customer_id": feedback.customer_id,
                    "product_id": feedback.product_id,
                    "is_delivery_issue": feedback.is_delivery_issue,
                    "is_collection_issue": feedback.is_collection_issue,
                    "description": feedback.description,
                    "translated_desc": feedback.translated_desc,
                    "created_at": feedback.created_at,
                    "updated_at": feedback.updated_at,
                    "created_by": feedback.created_by,
                    "user_id": feedback.user_id
                })
            
            return response_feedbacks
            
        except Exception as e:
            logger.error(f"Error getting feedbacks: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting feedbacks: {str(e)}"
            )