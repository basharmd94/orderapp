from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base
from datetime import datetime

# apiUsers table


class ApiUsers(Base):
    __tablename__ = "apiUsers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String,  index=True)
    password = Column(String)
    employee_name = Column(String, index=True)
    email = Column(String,  index=True)
    mobile = Column(String,index=True)
    businessId = Column(Integer)
    employeeCode = Column(String)
    terminal = Column(String)
    is_admin = Column(String)
    status = Column(String)
    accode = Column(String)



# logged table
class Logged(Base):
    __tablename__ = "logged"

    id = Column(Integer, primary_key=True, index=True)
    ztime = Column(DateTime, default=datetime.utcnow)
    zutime = Column(DateTime, default=datetime.utcnow)
    username = Column(String)
    businessId = Column(Integer)
    access_token = Column(String)
    refresh_token = Column(String)
    status = Column(String)


class Prmst(Base):
    __tablename__ = "prmst"

    zid = Column(Integer, primary_key=True, index=True)
    xemp = Column(String, index=True)
    xname = Column(String, index=True)
    xproj = Column(String)
    xstatusemp = Column(String)


