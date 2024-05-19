from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from uuid import uuid4

# class Base(DeclarativeBase):
#     pass


# class Prmst(Base):
#     __tablename__ = "prmst"

#     zid = Column(Integer, primary_key=True, index=True)
#     xemp = Column(String, index=True)
#     xname = Column(String, index=True)
#     xproj = Column(String)
#     xstatusemp = Column(String)


# engine = create_engine('postgresql://postgres:postgres@localhost/da_old')

# Session = sessionmaker(bind=engine)
# session = Session()

# # Query all data from prmst table
# result = session.query(Prmst).all()


# for row in result:
#     print(row.xname, row.xstatusemp)
# session.close()


x = uuid4()

print (x)