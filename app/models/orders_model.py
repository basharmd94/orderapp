from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger
from datetime import datetime
from database import Base


class Opmob(Base):
    __tablename__ = "opmob"

    zid = Column(Integer,  index=True)
    ztime = Column(DateTime, default=datetime.now)
    zutime = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    invoiceno = Column(String, index=True)
    invoicesl = Column(BigInteger)  # bigint
    username = Column(String, index=True)
    xemp = Column(String, index=True)
    xcus = Column(String)
    xcusname = Column(String)
    xcusadd = Column(String)
    xitem = Column(String)
    xdesc = Column(String)
    xqty = Column(Float)
    xprice = Column(Float)
    xstatusord = Column(String, nullable=True)
    xordernum = Column(String, nullable=True)
    xroword = Column(Integer)  # int
    xterminal = Column(String)
    xdate = Column(String)  # Assuming xdate is in "YYYY-MM-DD" format
    xsl = Column(String, primary_key=True)
    xlat = Column(Float)  # double precision
    xlong = Column(Float)  # double precision
    xlinetotal = Column(Float)
    xtra1 = Column(Integer)  # double precision
    xtra2 = Column(Float)
    xtra3 = Column(String, nullable=True)
    xtra4 = Column(String, nullable=True)
    xtra5 = Column(String, nullable=True)
