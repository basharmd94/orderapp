from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from datetime import datetime

# Many-to-Many relationship table for roles and permissions
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE')),
)

# Many-to-Many relationship table for users and roles
# Modified to use clearer column naming: 'username' instead of 'user_id'
user_role = Table(
    'user_role',
    Base.metadata,
    Column('username', String(50), ForeignKey('apiUsers.username', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
)

class Permission(Base):
    """
    Permission model for specific actions in the application
    """
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    codename = Column(String(100), unique=True, nullable=False)  # Machine-readable identifier
    description = Column(String(255))
    resource = Column(String(50), nullable=False)  # e.g. "orders", "customers", "items"
    action = Column(String(50), nullable=False)    # e.g. "create", "read", "update", "delete"
    
    # Relationships
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, codename={self.codename})>"

class Role(Base):
    """
    Role model for grouping permissions
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    is_default = Column(Boolean, default=False)
    created_at = Column(Integer)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    users = relationship("ApiUsers", secondary=user_role, back_populates="roles")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"