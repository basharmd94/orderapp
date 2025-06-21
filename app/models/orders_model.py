from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, Date
from datetime import datetime
from database import Base


class Opmob(Base):
    __tablename__ = "opmob"

    # Define columns with corresponding data types
    invoicesl = Column(BigInteger)
    xroword = Column(Integer)
    zutime = Column(DateTime)  # timestamp without time zone
    xdate = Column(Date)  # date
    xqty = Column(Integer)
    xlat = Column(Float)  # double precision
    xlong = Column(Float)  # double precision
    xlinetotal = Column(Integer)
    xtra1 = Column(Integer)
    xtra2 = Column(Float)  # double precision
    xprice = Column(Float)  # double precision
    ztime = Column(DateTime)  # timestamp without time zone
    zid = Column(Integer)
    xtra3 = Column(String)  # character varying
    xtra4 = Column(String)  # character varying
    xtra5 = Column(String)  # character varying
    invoiceno = Column(String)  # character varying
    username = Column(String)  # character varying
    xemp = Column(String)  # character varying
    xcus = Column(String)  # character varying
    xcusname = Column(String)  # character varying
    xcusadd = Column(String)  # character varying
    xitem = Column(String)  # character varying
    xdesc = Column(String)  # character varying
    xstatusord = Column(String, nullable=True)  # character varying
    xordernum = Column(String, nullable=True)  # character varying
    xterminal = Column(String)  # character varying
    xsl = Column(String, primary_key=True)  # character varying (primary key)


class Opord(Base):
    __tablename__ = "opord"
    __table_args__ = {'extend_existing': True}

    zid = Column(Integer)
    xdate = Column(Date)  # date
    xordernum = Column(String, primary_key=True)  # character varying
    xdate = Column(Date)  # date
    xcus = Column(String)  # character varying
    
class Opodt(Base):
    __tablename__ = "opodt"
    __table_args__ = {'extend_existing': True}

    zid = Column(Integer)
    xordernum = Column(String, primary_key=True)  # character varying
    xitem = Column(String)  # character varying
    xqty = Column(Integer)
    xlineamt = Column(Float)


# sales return model
class Opcrn(Base):
    __tablename__ = "opcrn"

    zid = Column(Integer)
    xcrnnum = Column(String, primary_key=True)  # character varying
    xcus = Column(String)  # character varying
    xdate = Column(String)  # character varying

class Opcdt(Base):
    __tablename__ = "opcdt"

    zid = Column(Integer)
    xcrnnum = Column(String, primary_key=True)  # character varying
    xitem = Column(String)  # character varying
    xqty = Column(Integer)
    xlineamt = Column(Float)


# damage return model

class Imtemptrn(Base):
    __tablename__ = "imtemptrn"

    zid = Column(Integer)
    ximtmptrn = Column(String, primary_key=True)  # character varying
    xqty = Column(Integer)
    xcus = Column(String)  # character varying
    xdate = Column(Date)  # date

class Imtemptdt(Base):
    __tablename__ = "imtemptdt"

    zid = Column(Integer)
    ximtmptrn = Column(String, primary_key=True)  # character varying
    xlineamt = Column(Float)  # double precision
