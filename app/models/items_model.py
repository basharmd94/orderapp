from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine,
    Numeric,
    ForeignKey,
    create_engine,
    func,
    Float,
    Numeric
)


class Caitem(Base):
    __tablename__ = "caitem"

    zid = Column(Integer, primary_key=True, index=True)
    xitem = Column(String, primary_key=True, index=True)
    xdesc = Column(String, index=True)
    xgitem = Column(String, index=True)
    xstdprice = Column(Numeric(10, 2))
    xunitstk = Column(String)


class Imtrn(Base):
    __tablename__ = "imtrn"

    zid = Column(Integer, primary_key=True, index=True)
    xitem = Column(String, ForeignKey("caitem.xitem"), primary_key=True, index=True)
    xqty = Column(Numeric(10, 2))
    xsign = Column(Integer)


class Opspprc(Base):
    __tablename__ = "opspprc"

    zid = Column(Integer, primary_key=True, index=True)
    xpricecat = Column(String, ForeignKey("caitem.xitem"), primary_key=True, index=True)
    xqty = Column(Numeric(10, 2))
    xdisc = Column(Numeric(10, 2))
