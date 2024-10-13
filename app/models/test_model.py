from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger, Date, TIMESTAMP
from datetime import datetime
from database import Base

class Abdef(Base):
    __tablename__ = "abdef"

    ztime = Column(TIMESTAMP)  # timestamp without time zone
    zutime = Column(TIMESTAMP)  # timestamp without time zone
    zid = Column(Integer , primary_key=True)  # integer
    xtitleord = Column(String)  # character varying
    xtitledor = Column(String)  # character varying
    xtitleinv = Column(String)  # character varying
    xtitlerec = Column(String)  # character varying
    xtitleart = Column(String)  # character varying
