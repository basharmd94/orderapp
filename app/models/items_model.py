
from database import Base
from sqlalchemy import Column, Integer, String

class Caitem(Base):

    __tablename__ = "caitem"

    xitem = Column(String, primary_key=True, nullable=False)
    xdesc = Column(String, nullable=False )