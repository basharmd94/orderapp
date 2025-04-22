from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, MetaData
from sqlalchemy.orm import declarative_base
from database import Base

class GLHeader(Base):
    __tablename__ = 'glheader'
    
    xvoucher = Column(String, primary_key=True)
    zid = Column(Integer, primary_key=True)
    xdate = Column(Date)

class GLDetail(Base):
    __tablename__ = 'gldetail'
    
    xvoucher = Column(String, primary_key=True)
    zid = Column(Integer, primary_key=True)
    xsub = Column(String, primary_key=True)
    xproj = Column(String)
    xprime = Column(Float)
