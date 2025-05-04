from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Feedback(Base):
    """Model for storing customer feedback data."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    zid = Column(Integer, primary_key=True)
    customer_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    is_delivery_issue = Column(Boolean, default=False)
    is_collection_issue = Column(Boolean, default=False)
    description = Column(Text, nullable=False)
    translated_desc = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String, ForeignKey("apiUsers.username"))
    user_id = Column(String)
    
    # Keep only the creator relationship
    creator = relationship("ApiUsers", backref="feedbacks")