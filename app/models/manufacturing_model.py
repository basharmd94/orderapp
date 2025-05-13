from database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey
)


class Moord(Base):
    """Manufacturing Order model representing the moord table in the database."""
    __tablename__ = "moord"

    zid = Column(Integer, primary_key=True, index=True)
    xmoord = Column(String, primary_key=True, index=True)
    xdatemo = Column(Date, index=True)
    xitem = Column(String, index=True)
    xqtyprd = Column(Numeric(10, 2))
    xunit = Column(String)
