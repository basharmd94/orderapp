from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.users_model import ApiUsers, Logged, SessionHistory, Prmst
from logs import setup_logger
from datetime import datetime
from utils.token_utils import blacklist_token
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

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
                    self.db.add(session_history)                # Delete all logged sessions
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
            
    async def update_user(self, user_data):
        """Update user information"""
        try:
            # Get the user
            result = await self.db.execute(
                select(ApiUsers).filter(ApiUsers.username == user_data.username)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_data.username} not found"
                )

            # Check if email is being updated and if it's already in use by another user
            if user_data.email != user.email:
                email_check = await self.db.execute(
                    select(ApiUsers).filter(
                        ApiUsers.email == user_data.email,
                        ApiUsers.username != user_data.username
                    )
                )
                existing_email = email_check.scalar_one_or_none()
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use by another user"
                    )
            
            # Check if user_id is being updated and if it's valid
            if user_data.user_id and user_data.user_id != user.employeeCode:
                # Check if the user_id exists in Prmst
                prmst_check = await self.db.execute(
                    select(ApiUsers.__table__.c).select_from(
                        ApiUsers.__table__
                    ).where(
                        ApiUsers.employeeCode == user_data.user_id,
                        ApiUsers.username != user_data.username
                    )
                )
                existing_user_id = prmst_check.scalar_one_or_none()
                if existing_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Employee ID already in use by another user"
                    )

            # Update user fields
            user.email = user_data.email
            
            if user_data.mobile is not None:
                user.mobile = user_data.mobile
            
            if user_data.user_id is not None:
                user.employeeCode = user_data.user_id.upper()
            
            if user_data.status is not None:
                user.status = user_data.status
            
            if user_data.businessId is not None:
                user.businessId = user_data.businessId
                
                # Update accode based on businessId
                if user_data.businessId == 100000:
                    user.accode = "a"
                elif user_data.businessId == 100001:
                    user.accode = "b"
                elif user_data.businessId == 100005:
                    user.accode = "c"
            
            if user_data.is_admin is not None:
                user.is_admin = user_data.is_admin
            
            # Handle password update if provided
            if user_data.password is not None:
                # Validate password length
                if len(user_data.password) < 4:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password must be at least 4 characters long"
                    )
                # Hash the password
                hashed_password = pwd_context.hash(user_data.password)
                user.password = hashed_password

            await self.db.commit()
            
            # Return updated user data
            return {
                "username": user.username,
                "email": user.email,
                "mobile": user.mobile,
                "employeeCode": user.employeeCode,
                "status": user.status,
                "businessId": user.businessId,
                "is_admin": user.is_admin,
                "message": f"User {user.username} updated successfully"
            }

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error occurred while updating user information"
            )