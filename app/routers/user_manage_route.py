from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.db_controllers.user_manage_controller import UserManageController
from controllers.db_controllers.user_db_controller import UserDBController
from schemas.user_manage_schema import UserStatusUpdate, UserUpdate
from schemas.user_schema import UserOutSchema
from utils.auth import get_current_admin
from logs import setup_logger
from typing import List
from models.users_model import ApiUsers

router = APIRouter(
    prefix="/user-manage",
    tags=["User Management"],
    dependencies=[Depends(get_current_admin)],  # All routes require admin access
)

logger = setup_logger()

@router.delete("/{username}")
async def delete_user(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a user and all their associated data"""
    user_controller = UserManageController(db)
    return await user_controller.delete_user(username)

@router.post("/status")
async def update_user_status(
    user_status: UserStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a user's status (active/inactive)"""
    user_controller = UserManageController(db)
    return await user_controller.update_user_status(
        username=user_status.username,
        new_status=user_status.status
    )

@router.get("/get-all-users", response_model=List[UserOutSchema])
async def get_all_users(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users from the system.
    Only accessible by admin users.
    """
    try:
        user_db = UserDBController(db)
        users = await user_db.get_all_users()
        # Convert ApiUsers to UserOutSchema format
        user_list = []
        for user in users:
            user_dict = {
                "username": user.username,
                "email": user.email,
                "mobile": user.mobile,
                "status": user.status,
                "businessId": user.businessId,
                "terminal": user.terminal,
                "accode": user.accode,
                "is_admin": user.is_admin,
                "employee_name": user.employee_name,
                "user_id": user.employeeCode  # Map employeeCode to user_id
            }
            user_list.append(user_dict)
        return user_list
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )

@router.put("/update-user")
async def update_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Update user information
    Requires admin privileges
    """
    try:
        user_controller = UserManageController(db)
        return await user_controller.update_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_user endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating user"
        )