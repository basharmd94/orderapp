from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import selectinload

from models.permissions_model import Permission, Role
from models.users_model import ApiUsers
from logs import setup_logger

logger = setup_logger()

class RBACController:
    """Controller for managing roles, permissions, and user roles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_permission(self, name: str, codename: str, resource: str, action: str, description: Optional[str] = None) -> Permission:
        """
        Create a new permission
        
        Args:
            name: Human-readable name of the permission
            codename: Machine-readable identifier 
            resource: The resource this permission applies to (e.g., "orders")
            action: The action allowed on the resource (e.g., "create", "read")
            description: Optional description of what this permission allows
            
        Returns:
            The created Permission object
        """
        try:
            # Check if permission with this codename already exists
            exists = await self.db.execute(
                select(Permission).filter(Permission.codename == codename)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission with codename '{codename}' already exists"
                )
                
            # Create new permission
            permission = Permission(
                name=name,
                codename=codename,
                resource=resource,
                action=action,
                description=description
            )
            
            self.db.add(permission)
            await self.db.commit()
            await self.db.refresh(permission)
            
            logger.info(f"Created permission: {codename}")
            return permission
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create permission"
            )
            
    async def create_role(self, name: str, description: Optional[str] = None, is_default: bool = False) -> Role:
        """
        Create a new role
        
        Args:
            name: Name of the role
            description: Optional description of the role
            is_default: Whether this is a default role assigned to new users
            
        Returns:
            The created Role object
        """
        try:
            # Check if role with this name already exists
            exists = await self.db.execute(
                select(Role).filter(Role.name == name)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role with name '{name}' already exists"
                )
                
            # Create new role
            role = Role(
                name=name,
                description=description,
                is_default=is_default
            )
            
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            
            logger.info(f"Created role: {name}")
            return role
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create role"
            )
            
    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> Role:
        """
        Assign a permission to a role
        
        Args:
            role_id: ID of the role
            permission_id: ID of the permission
            
        Returns:
            Updated Role object
        """
        try:
            # Get role and permission
            role_result = await self.db.execute(
                select(Role).filter(Role.id == role_id)
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role with ID {role_id} not found"
                )
                
            permission_result = await self.db.execute(
                select(Permission).filter(Permission.id == permission_id)
            )
            permission = permission_result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Permission with ID {permission_id} not found"
                )
                
            # Check if permission is already assigned to role
            if permission in role.permissions:
                logger.info(f"Permission {permission.codename} is already assigned to role {role.name}")
                return role
                
            # Assign permission to role
            role.permissions.append(permission)
            await self.db.commit()
            await self.db.refresh(role)
            
            logger.info(f"Assigned permission {permission.codename} to role {role.name}")
            return role
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error assigning permission to role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign permission to role"
            )
            
    async def assign_role_to_user(self, username: str, role_id: int) -> ApiUsers:
        """
        Assign a role to a user
        
        Args:
            username: Username of the user
            role_id: ID of the role
            
        Returns:
            Updated ApiUsers object
        """
        try:
            # Get user and role
            user_result = await self.db.execute(
                select(ApiUsers).filter(ApiUsers.username == username)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )
                
            role_result = await self.db.execute(
                select(Role).filter(Role.id == role_id)
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role with ID {role_id} not found"
                )
                
            # Check if role is already assigned to user
            if role in user.roles:
                logger.info(f"Role {role.name} is already assigned to user {username}")
                return user
                
            # Assign role to user
            user.roles.append(role)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Assigned role {role.name} to user {username}")
            return user
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error assigning role to user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign role to user"
            )
    
    async def get_user_permissions(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all permissions for a user
        
        Args:
            username: Username of the user
            
        Returns:
            List of permission dictionaries
        """
        try:
            # Get user with roles relationship eagerly loaded
            stmt = (
                select(ApiUsers)
                .filter(ApiUsers.username == username)
                .options(
                    selectinload(ApiUsers.roles).selectinload(Role.permissions)
                )
            )
            user_result = await self.db.execute(stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )
                
            # Admin users have all permissions
            if user.is_admin and user.is_admin.lower() == "admin":
                # Get all permissions in a single query
                permission_result = await self.db.execute(select(Permission))
                permissions = permission_result.scalars().all()
                
                return [{
                    "id": perm.id,
                    "name": perm.name,
                    "codename": perm.codename,
                    "resource": perm.resource,
                    "action": perm.action,
                    "description": perm.description
                } for perm in permissions]
            
            # Handle users with no roles
            if not user.roles:
                logger.info(f"User {username} has no roles assigned")
                return []
                
            # Collect unique permissions from user roles
            user_permissions = set()
            for role in user.roles:
                for permission in role.permissions:
                    user_permissions.add(permission)
                    
            return [{
                "id": perm.id,
                "name": perm.name,
                "codename": perm.codename,
                "resource": perm.resource,
                "action": perm.action,
                "description": perm.description
            } for perm in user_permissions]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user permissions"
            )
    
    async def remove_role_from_user(self, username: str, role_id: int) -> ApiUsers:
        """
        Remove a role from a user
        
        Args:
            username: Username of the user
            role_id: ID of the role
            
        Returns:
            Updated ApiUsers object
        """
        try:
            # Get user and role
            user_result = await self.db.execute(
                select(ApiUsers).filter(ApiUsers.username == username)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )
                
            role_result = await self.db.execute(
                select(Role).filter(Role.id == role_id)
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role with ID {role_id} not found"
                )
                
            # Check if role is assigned to user
            if role not in user.roles:
                logger.info(f"Role {role.name} is not assigned to user {username}")
                return user
                
            # Remove role from user
            user.roles.remove(role)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Removed role {role.name} from user {username}")
            return user
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error removing role from user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove role from user"
            )