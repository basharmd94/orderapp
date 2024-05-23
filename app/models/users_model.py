from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base
from datetime import datetime

# apiUsers table


class ApiUsers(Base):
    __tablename__ = "apiUsers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    employee_name = Column(String)
    email = Column(String, unique=True, index=True)
    mobile = Column(String)
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


class UrlRoutes(Base):
    __tablename__ = "urlroutes"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    zid = Column(String, index=True)
    routes = Column( String)
    urldb = Column(String)
    acodes = Column(String)
