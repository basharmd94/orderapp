from sqlalchemy import Column, Integer, String, create_engine,  ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from uuid import uuid4

class Base(DeclarativeBase):
    pass


engine = create_engine('postgresql://postgres:postgres@localhost/da_old')

Session = sessionmaker(bind=engine)
session = Session()



class Caitem(Base):
    __tablename__ = 'caitem'
    
    zid = Column(Integer, primary_key=True, index=True)
    xitem = Column(String, primary_key=True, index=True)
    xdesc = Column(String)
    xgitem = Column(String)
    xstdprice = Column(Integer)
    xunitstk = Column(String)

class Imtrn(Base):
    __tablename__ = 'imtrn'
    
    zid = Column(Integer, primary_key=True, index=True)
    xitem = Column(String, ForeignKey('caitem.xitem'), primary_key=True, index=True)
    xqty = Column(Integer)
    xsign = Column(Integer)




class Opspprc(Base):
    __tablename__ = 'opspprc'
    
    zid = Column(Integer, primary_key=True, index=True)
    xpricecat = Column(String, ForeignKey('caitem.xitem'), primary_key=True, index=True)
    xqty = Column(Integer)
    xdisc = Column(Integer)
# The main query using the CTE

# Define CTE for transaction summary
transaction_summary = (
    session.query(
        Imtrn.xitem,
        func.sum(Imtrn.xqty * Imtrn.xsign).label('stock')
    )
    .filter(Imtrn.zid == 100001)
    .group_by(Imtrn.xitem)
    .cte('transaction_summary')
)


query = (
    session.query(
        Caitem.xitem,
        Caitem.xdesc,
        Caitem.xgitem,
        Caitem.xstdprice,
        Caitem.xunitstk,
        transaction_summary.c.stock,
        Opspprc.xqty.label('min_disc_qty'),
        Opspprc.xdisc.label('disc_amt')
    )
    .join(transaction_summary, Caitem.xitem == transaction_summary.c.xitem)
    .join(Opspprc, Caitem.xitem == Opspprc.xpricecat)
    .filter(
        Caitem.zid == 100001,
        Opspprc.zid == 100001,
        transaction_summary.c.stock > 0
    )
    .group_by(
        Caitem.xitem,
        Caitem.xdesc,
        Caitem.xgitem,
        Caitem.xstdprice,
        Caitem.xunitstk,
        Opspprc.xqty,
        Opspprc.xdisc,
        transaction_summary.c.stock
    )
    .limit(10)
    .offset(100)
)

# Execute the query and fetch results
results = query.all()

# Print results
for result in results:
    print(result)