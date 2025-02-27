from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import validates
from sqlalchemy import event
from database import Base
from datetime import datetime

from logs import setup_logger
import traceback

# apiUsers table


logger = setup_logger()

class ApiUsers(Base):
    __tablename__ = "apiUsers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String,  index=True)
    password = Column(String)
    employee_name = Column(String, index=True)
    email = Column(String,  index=True)
    mobile = Column(String,index=True)
    businessId = Column(Integer)  # Changed to Integer type
    employeeCode = Column(String)
    terminal = Column(String)
    is_admin = Column(String)  # Must contain 'admin', 'user', or empty string
    status = Column(String)
    accode = Column(String)  # This limits the column to 50 characters

#     @validates('is_admin')
#     def validate_is_admin(self, key, value):
#         if isinstance(value, bool):
#             return 'admin' if value else 'user'
#         if value not in ['admin', 'user', '']:
#             raise ValueError(f"is_admin must be 'admin', 'user', or '', got {value} of type {type(value)}")
#         return value

# @event.listens_for(ApiUsers.is_admin, 'set', retval=True)
# def receive_set(target, value, oldvalue, initiator):
#     logger.debug(f"Setting is_admin value: {value} (type: {type(value)})")
#     logger.debug(f"Previous is_admin value: {oldvalue} (type: {type(oldvalue)})")
#     logger.debug(f"Stack trace for is_admin setting:\n{traceback.format_stack()}")
    
#     if isinstance(value, bool):
#         new_value = 'admin' if value else 'user'
#         logger.warning(f"Converting boolean is_admin value {value} to string: {new_value}")
#         return new_value
#     return value

# logged table
class Logged(Base):
    __tablename__ = "logged"

    id = Column(Integer, primary_key=True, index=True)
    ztime = Column(DateTime, default=datetime.utcnow)
    zutime = Column(DateTime, default=datetime.utcnow)
    username = Column(String)
    businessId = Column(Integer)
    access_token = Column(String(1000))  # Increased length for JWT tokens
    refresh_token = Column(String(1000))  # Increased length for JWT tokens
    status = Column(String)
    device_info = Column(String)  # To track device information
    is_admin = Column(String)  # Added is_admin field


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(1000), unique=True, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    
class Prmst(Base):
    __tablename__ = "prmst"

    zid = Column(Integer, primary_key=True, index=True)
    xemp = Column(String, index=True)
    xname = Column(String, index=True)
    xproj = Column(String)
    xstatusemp = Column(String)

class SessionHistory(Base):
    __tablename__ = "session_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    businessId = Column(Integer)
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    device_info = Column(String)
    status = Column(String)  # "Completed", "Forced Logout", "Expired", etc.
    access_token = Column(String(1000))
    refresh_token = Column(String(1000))
    is_admin = Column(String)  # Added is_admin field

class LoginAttempts(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    attempt_time = Column(DateTime, default=datetime.utcnow)
    attempt_count = Column(Integer, default=1)
    locked_until = Column(DateTime, nullable=True)
    ip_address = Column(String)


