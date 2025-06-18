from database import Base
from sqlalchemy import Column, Integer, String, func


class Cacus(Base):
    __tablename__ = "cacus"

    zid = Column(Integer, primary_key=True, index=True)
    xcus = Column(String, primary_key=True, index=True)
    xorg = Column(String)
    xadd1 = Column(String)
    xcity = Column(String, index=True)
    xstate = Column(String, index=True)
    xmobile = Column(String, index=True)
    xtaxnum = Column(String, index=True)
    xsp = Column(String, index=True)
    xsp1 = Column(String, index=True)
    xsp2 = Column(String, index=True)
    xsp3 = Column(String, index=True)
    # For Offer Columns
    xtitle = Column(String, ) # Here will retrive the current customer's segment title
    xfax = Column(String, ) # Here will retrive the current customer's segmentation score number between 0.0 to 1.0
    xcreditr = Column(String, ) # Here will retrive the current customer's offer receiving 
    
 