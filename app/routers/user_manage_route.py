from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.db_controllers.user_manage_controller import UserManageController
from schemas.user_manage_schema import UserStatusUpdate
from utils.auth import get_current_admin
from logs import setup_logger

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