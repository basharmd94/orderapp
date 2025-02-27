from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from controllers.db_controllers.rbac_controller import RBACController
from schemas.user_schema import UserRegistrationSchema
from utils.auth import get_current_admin
from logs import setup_logger
from utils.permissions import has_permission
from schemas.order_stats_schema import BaseResponse

# Create schemas for RBAC endpoints
from pydantic import BaseModel, Field

# Role schema models
class RoleCreate(BaseModel):
    name: str = Field(..., description="Name of the role")
    description: Optional[str] = Field(None, description="Description of the role")
    is_default: bool = Field(False, description="Whether this is a default role for new users")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "content_editor",
                "description": "Can edit content but not delete it",
                "is_default": False
            }
        }

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_default: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 5,
                "name": "content_editor",
                "description": "Can edit content but not delete it",
                "is_default": False
            }
        }

# Permission schema models
class PermissionCreate(BaseModel):
    name: str = Field(..., description="Human-readable name of the permission")
    codename: str = Field(..., description="Machine-readable identifier for the permission")
    resource: str = Field(..., description="Resource this permission applies to (e.g., 'orders')")
    action: str = Field(..., description="Action allowed on the resource (e.g., 'create')")
    description: Optional[str] = Field(None, description="Description of what this permission allows")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Export Reports",
                "codename": "report.export",
                "resource": "reports",
                "action": "export",
                "description": "Can export reports to CSV/PDF formats"
            }
        }

class PermissionResponse(BaseModel):
    id: int
    name: str
    codename: str
    resource: str
    action: str
    description: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 25,
                "name": "Export Reports",
                "codename": "report.export",
                "resource": "reports",
                "action": "export",
                "description": "Can export reports to CSV/PDF formats"
            }
        }

# Role-Permission assignment schema
class RolePermissionAssign(BaseModel):
    role_id: int = Field(..., description="ID of the role")
    permission_id: int = Field(..., description="ID of the permission")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role_id": 3,
                "permission_id": 7
            }
        }

# User-Role assignment schema
class UserRoleAssign(BaseModel):
    username: str = Field(..., description="Username of the user")
    role_id: int = Field(..., description="ID of the role")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "role_id": 3
            }
        }

logger = setup_logger()

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    }
)

@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
    description="Creates a new permission that can be assigned to roles"
)
async def create_permission(
    permission: PermissionCreate,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new permission"""
    rbac_controller = RBACController(db)
    new_permission = await rbac_controller.create_permission(
        name=permission.name,
        codename=permission.codename,
        resource=permission.resource,
        action=permission.action,
        description=permission.description
    )
    return new_permission

@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    description="Creates a new role that can be assigned to users"
)
async def create_role(
    role: RoleCreate,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new role"""
    rbac_controller = RBACController(db)
    new_role = await rbac_controller.create_role(
        name=role.name,
        description=role.description,
        is_default=role.is_default
    )
    return new_role

@router.post(
    "/roles/permissions",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign a permission to a role",
    description="Assigns a permission to a role"
)
async def assign_permission_to_role(
    assignment: RolePermissionAssign,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Assign a permission to a role"""
    rbac_controller = RBACController(db)
    updated_role = await rbac_controller.assign_permission_to_role(
        role_id=assignment.role_id,
        permission_id=assignment.permission_id
    )
    return updated_role

@router.post(
    "/users/roles",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign a role to a user",
    description="Assigns a role to a user"
)
async def assign_role_to_user(
    assignment: UserRoleAssign,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Assign a role to a user"""
    rbac_controller = RBACController(db)
    await rbac_controller.assign_role_to_user(
        username=assignment.username,
        role_id=assignment.role_id
    )
    return BaseResponse(message="Role assigned successfully to user")

@router.delete(
    "/users/roles",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove a role from a user",
    description="Removes a role from a user"
)
async def remove_role_from_user(
    assignment: UserRoleAssign,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Remove a role from a user"""
    rbac_controller = RBACController(db)
    await rbac_controller.remove_role_from_user(
        username=assignment.username,
        role_id=assignment.role_id
    )
    return BaseResponse(message="Role removed successfully from user")

@router.get(
    "/users/{username}/permissions",
    status_code=status.HTTP_200_OK,
    summary="Get permissions for a user",
    description="Returns all permissions a user has through their roles"
)
async def get_user_permissions(
    username: str,
    request: Request,
    current_user: UserRegistrationSchema = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get permissions for a user
    
    Example response:
    ```json
    {
      "permissions": [
        {
          "id": 1,
          "name": "Create Order",
          "codename": "order.create",
          "resource": "orders",
          "action": "create",
          "description": "Can create new orders"
        },
        {
          "id": 2,
          "name": "View Orders",
          "codename": "order.view",
          "resource": "orders",
          "action": "read",
          "description": "Can view orders"
        }
      ]
    }
    ```
    """
    rbac_controller = RBACController(db)
    permissions = await rbac_controller.get_user_permissions(username=username)
    return {"permissions": permissions}