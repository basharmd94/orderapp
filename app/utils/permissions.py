from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Union, Callable, Any
import functools
from jose import jwt
import inspect

from logs import setup_logger
from database import get_db
from models.permissions_model import Permission, Role
from models.users_model import ApiUsers
from utils.auth import get_current_user
from utils.token_utils import SECRET_KEY, ALGORITHM

logger = setup_logger()

async def check_user_permissions(
    db: AsyncSession, 
    username: str, 
    required_permissions: List[str]
) -> bool:
    """
    Check if a user has the required permissions either through direct role assignment
    or inherited from roles.
    
    Args:
        db: Database session
        username: Username to check permissions for
        required_permissions: List of permission codenames to check
        
    Returns:
        bool: True if user has all required permissions, False otherwise
    """
    try:
        # Get the user with their roles
        user_query = await db.execute(
            select(ApiUsers).filter(ApiUsers.username == username)
        )
        user = user_query.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Permission check failed: User {username} not found")
            return False
            
        # Admin users always have all permissions
        if user.is_admin and user.is_admin.lower() == "admin":
            logger.info(f"User {username} has admin status, granting all permissions")
            return True
            
        # Get all permissions for the user's roles
        if not user.roles:
            logger.warning(f"User {username} has no roles assigned")
            return False
            
        # Collect all permissions from the user's roles
        user_permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.codename)
                
        # Check if the user has all the required permissions
        has_permissions = all(perm in user_permissions for perm in required_permissions)
        
        if not has_permissions:
            logger.warning(f"User {username} lacks required permissions: {required_permissions}")
        else:
            logger.info(f"Permission check successful for user {username}: {required_permissions}")
            
        return has_permissions
        
    except Exception as e:
        logger.error(f"Error checking permissions for {username}: {str(e)}")
        return False


def has_permission(required_permissions: Union[str, List[str]]):
    """
    Decorator to check if user has the required permission(s) to access an endpoint.
    
    Args:
        required_permissions: Single permission string or list of permission strings
    """
    if isinstance(required_permissions, str):
        required_permissions = [required_permissions]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
            if not request and "request" in kwargs:
                request = kwargs["request"]
                
            # Get current_user from the function's dependencies
            current_user = None
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name in kwargs and hasattr(kwargs[param_name], "user_name"):
                    current_user = kwargs[param_name]
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Get database session from the function's dependencies
            db = None
            for key, val in kwargs.items():
                if isinstance(val, AsyncSession):
                    db = val
                    break
                    
            if not db:
                # Get db from dependency if not found in kwargs
                db = await get_db().__anext__()
                
            username = current_user.user_name
            has_perm = await check_user_permissions(db, username, required_permissions)
            
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: {', '.join(required_permissions)}"
                )
                
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator


def has_role(required_roles: Union[str, List[str]]):
    """
    Decorator to check if user has the required role(s) to access an endpoint.
    
    Args:
        required_roles: Single role name or list of role names
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
                    
            if not request and "request" in kwargs:
                request = kwargs["request"]
                
            # Get current_user from the function's dependencies
            current_user = None
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name in kwargs and hasattr(kwargs[param_name], "user_name"):
                    current_user = kwargs[param_name]
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Get database session from the function's dependencies
            db = None
            for key, val in kwargs.items():
                if isinstance(val, AsyncSession):
                    db = val
                    break
                    
            if not db:
                # Get db from dependency if not found in kwargs
                db = await get_db().__anext__()
                
            # Admin users have access to all roles
            if current_user.is_admin == "admin":
                return await func(*args, **kwargs)
                
            # Get user with roles from database
            username = current_user.user_name
            user_query = await db.execute(
                select(ApiUsers).filter(ApiUsers.username == username)
            )
            user = user_query.scalar_one_or_none()
            
            if not user or not user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User has no roles assigned"
                )
                
            user_role_names = {role.name for role in user.roles}
            if not any(role in user_role_names for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role not found: {', '.join(required_roles)}"
                )
                
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator