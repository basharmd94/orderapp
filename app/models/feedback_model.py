from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# Association table for many-to-many relationship between feedback and customers
feedback_customer_association = Table(
    'feedback_customer_association',
    Base.metadata,
    Column('feedback_id', Integer, ForeignKey('feedback.id', ondelete='CASCADE'), primary_key=True),
    Column('zid', Integer, ForeignKey('feedback.zid', ondelete='CASCADE'), primary_key=True),
    Column('customer_id', String, ForeignKey('cacus.xcus', ondelete='CASCADE'), primary_key=True)
)

# Association table for many-to-many relationship between feedback and products
feedback_product_association = Table(
    'feedback_product_association',
    Base.metadata,
    Column('feedback_id', Integer, ForeignKey('feedback.id', ondelete='CASCADE'), primary_key=True),
    Column('zid', Integer, ForeignKey('feedback.zid', ondelete='CASCADE'), primary_key=True),
    Column('product_id', String, ForeignKey('caitem.xitem', ondelete='CASCADE'), primary_key=True)
)

class Feedback(Base):
    """Model for storing customer feedback data."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    zid = Column(Integer, primary_key=True)
    is_delivery_issue = Column(Boolean, default=False)
    is_collection_issue = Column(Boolean, default=False)
    description = Column(Text, nullable=False)
    translated_desc = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String, ForeignKey("apiUsers.username"))
    user_id = Column(String)
    
    # Define relationships with explicit foreign keys
    customers = relationship(
        "Cacus", 
        secondary=feedback_customer_association,
        primaryjoin="and_(Feedback.id==feedback_customer_association.c.feedback_id, Feedback.zid==feedback_customer_association.c.zid)",
        secondaryjoin="Cacus.xcus==feedback_customer_association.c.customer_id",
        foreign_keys=[
            feedback_customer_association.c.feedback_id,
            feedback_customer_association.c.zid,
            feedback_customer_association.c.customer_id
        ]
    )
    
    products = relationship(
        "Caitem", 
        secondary=feedback_product_association,
        primaryjoin="and_(Feedback.id==feedback_product_association.c.feedback_id, Feedback.zid==feedback_product_association.c.zid)",
        secondaryjoin="Caitem.xitem==feedback_product_association.c.product_id",
        foreign_keys=[
            feedback_product_association.c.feedback_id,
            feedback_product_association.c.zid,
            feedback_product_association.c.product_id
        ]
    )
    
    creator = relationship("ApiUsers", backref="feedbacks")