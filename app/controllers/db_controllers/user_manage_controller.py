from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.users_model import ApiUsers, Logged, SessionHistory
from logs import setup_logger
from datetime import datetime
from utils.token_utils import blacklist_token

logger = setup_logger()

class UserManageController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_user(self, username: str):
        """Delete a user and their associated data"""
        try:
            # First get all user sessions to get their tokens
            sessions = await self.db.execute(
                select(Logged).filter(Logged.username == username)
            )
            user_sessions = sessions.scalars().all()

            # Blacklist all tokens
            for session in user_sessions:
                await blacklist_token(self.db, session.access_token)
                if session.refresh_token:
                    await blacklist_token(self.db, session.refresh_token)

                # Create session history record for each logged session
                session_history = SessionHistory(
                    username=session.username,
                    businessId=session.businessId,
                    login_time=session.ztime,
                    logout_time=datetime.utcnow(),
                    device_info=session.device_info,
                    status="User Deleted",
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    is_admin=session.is_admin
                )
                self.db.add(session_history)

            # Delete all logged sessions
            await self.db.execute(
                Logged.__table__.delete().where(Logged.username == username)
            )

            # Delete the user from apiUsers
            result = await self.db.execute(
                ApiUsers.__table__.delete().where(ApiUsers.username == username)
            )

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )

            await self.db.commit()
            return {"message": f"User {username} and associated data deleted successfully"}

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error occurred while deleting user"
            )

    async def update_user_status(self, username: str, new_status: str):
        """Update user status and handle related operations"""
        try:
            # Get the user
            result = await self.db.execute(
                select(ApiUsers).filter(ApiUsers.username == username)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {username} not found"
                )

            # Update user status
            user.status = new_status.lower()

            # If status is inactive, log out all sessions
            if new_status.lower() == "inactive":
                # Get all active sessions
                sessions = await self.db.execute(
                    select(Logged).filter(Logged.username == username)
                )
                user_sessions = sessions.scalars().all()

                # Handle each session
                for session in user_sessions:
                    # Blacklist tokens
                    await blacklist_token(self.db, session.access_token)
                    if session.refresh_token:
                        await blacklist_token(self.db, session.refresh_token)

                    # Create session history record
                    session_history = SessionHistory(
                        username=session.username,
                        businessId=session.businessId,
                        login_time=session.ztime,
                        logout_time=datetime.utcnow(),
                        device_info=session.device_info,
                        status="Status Changed to Inactive",
                        access_token=session.access_token,
                        refresh_token=session.refresh_token,
                        is_admin=session.is_admin
                    )
                    self.db.add(session_history)

                # Delete all logged sessions
                await self.db.execute(
                    Logged.__table__.delete().where(Logged.username == username)
                )

            await self.db.commit()
            return {"message": f"User {username} status updated to {new_status}"}

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error occurred while updating user status"
            )