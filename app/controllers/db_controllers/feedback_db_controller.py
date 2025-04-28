from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import selectinload
from models.feedback_model import Feedback, feedback_customer_association, feedback_product_association
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
        """Create a new feedback entry with associated customers and products."""
        if self.db is None:
            raise Exception("Database session not initialized.")
        
        try:
            # Create feedback object with base data
            new_feedback = Feedback(
                zid=feedback_data.zid,
                is_delivery_issue=feedback_data.is_delivery_issue,
                is_collection_issue=feedback_data.is_collection_issue,
                description=feedback_data.description,
                created_by=username,
                user_id=feedback_data.user_id
            )
            
            # Get customers
            customers_result = await self.db.execute(
                select(Cacus).filter(
                    and_(
                        Cacus.zid == feedback_data.zid,
                        Cacus.xcus.in_(feedback_data.customer_ids)
                    )
                )
            )
            customers_list = customers_result.scalars().all()
            
            if len(customers_list) != len(feedback_data.customer_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"One or more customers not found in business {feedback_data.zid}"
                )
            
            # Get products
            products_result = await self.db.execute(
                select(Caitem).filter(
                    and_(
                        Caitem.zid == feedback_data.zid,
                        Caitem.xitem.in_(feedback_data.product_ids)
                    )
                )
            )
            products_list = products_result.scalars().all()
            
            if len(products_list) != len(feedback_data.product_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"One or more products not found in business {feedback_data.zid}"
                )
            
            # Store the IDs before assigning to avoid async lazy loading issues
            customer_ids = [customer.xcus for customer in customers_list]
            product_ids = [product.xitem for product in products_list]
            
            # Assign relationships
            new_feedback.customers = customers_list
            new_feedback.products = products_list
            
            # Add to session and commit
            self.db.add(new_feedback)
            await self.db.commit()
            await self.db.refresh(new_feedback)
            
            # Return dictionary with all needed fields instead of the entity
            return {
                "id": new_feedback.id,
                "zid": new_feedback.zid,
                "is_delivery_issue": new_feedback.is_delivery_issue,
                "is_collection_issue": new_feedback.is_collection_issue,
                "description": new_feedback.description,
                "translated_desc": new_feedback.translated_desc,
                "created_at": new_feedback.created_at,
                "updated_at": new_feedback.updated_at,
                "created_by": new_feedback.created_by,
                "user_id": new_feedback.user_id,
                "customer_ids": customer_ids,
                "product_ids": product_ids
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
            # Start building the query with eager loading
            query = select(Feedback).options(
                selectinload(Feedback.customers),
                selectinload(Feedback.products)
            )
            
            # Apply filters if provided
            if query_params.zid is not None:
                query = query.filter(Feedback.zid == query_params.zid)
                
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
            
            # Filter by specific customer if provided
            if query_params.customer_id is not None:
                query = query.join(feedback_customer_association).filter(
                    feedback_customer_association.c.customer_id == query_params.customer_id
                )
            
            # Filter by specific product if provided
            if query_params.product_id is not None:
                query = query.join(feedback_product_association).filter(
                    feedback_product_association.c.product_id == query_params.product_id
                )
            
            # Add ordering, limit and offset
            query = query.order_by(Feedback.created_at.desc())
            
            if query_params.limit is not None:
                query = query.limit(query_params.limit)
                
            if query_params.offset is not None:
                query = query.offset(query_params.offset)
            
            # Execute the query
            result = await self.db.execute(query)
            feedbacks = result.unique().scalars().all()
            
            # Convert to response format
            response_feedbacks = []
            for feedback in feedbacks:
                # Access relationships inside the async context
                customer_ids = [customer.xcus for customer in feedback.customers]
                product_ids = [product.xitem for product in feedback.products]
                
                response_feedbacks.append({
                    "id": feedback.id,
                    "zid": feedback.zid,
                    "is_delivery_issue": feedback.is_delivery_issue,
                    "is_collection_issue": feedback.is_collection_issue,
                    "description": feedback.description,
                    "translated_desc": feedback.translated_desc,
                    "created_at": feedback.created_at,
                    "updated_at": feedback.updated_at,
                    "created_by": feedback.created_by,
                    "user_id": feedback.user_id,
                    "customer_ids": customer_ids,
                    "product_ids": product_ids
                })
            
            return response_feedbacks
            
        except Exception as e:
            logger.error(f"Error getting feedbacks: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting feedbacks: {str(e)}"
            )