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


# final items view table. 



class FinalItemsView(Base):
    __tablename__ = 'final_items_view'
    
    # Define the columns for the view
    zid = Column(Integer, primary_key=True, index=True)
    item_id = Column(String)
    item_name = Column(String)
    item_group = Column(String)
    std_price = Column(Numeric)
    stock = Column(Numeric)
    min_disc_qty = Column(Numeric)
    disc_amt = Column(Numeric)

    # Just omit any primary key declaration for views without one
    # SQLAlchemy will handle it without the need for `primary_key=False`

    __table_args__ = (
        {"comment": "View without a primary key"},
    )