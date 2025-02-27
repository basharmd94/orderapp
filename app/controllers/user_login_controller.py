
from fastapi import HTTPException, status, Form, Request
from models.users_model import ApiUsers, Logged, TokenBlacklist, SessionHistory, LoginAttempts
from fastapi.security import OAuth2PasswordRequestForm
from utils.error import error_details
from utils.token_utils import (
    create_access_token, create_refresh_token, blacklist_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from passlib.context import CryptContext

from logs import setup_logger
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_TIME_SECONDS = int(os.getenv("LOCKOUT_TIME_SECONDS", "300"))  # 5 minutes

# Initialize password context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

logger = setup_logger()

class UserLoginController:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def cleanup_inactive_sessions(self, max_inactive_hours: int = 720):
        """Cleanup sessions that have been inactive for longer than the specified hours"""
        try:
            # For login we use a shorter timeout (30 minutes)
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            if max_inactive_hours > 0:  # If specifically called with hours parameter
                cutoff_time = datetime.utcnow() - timedelta(hours=max_inactive_hours)
            
            # Find inactive sessions
            result = await self.db.execute(
                select(Logged).filter(Logged.zutime < cutoff_time)
            )
            inactive_sessions = result.scalars().all()

            for session in inactive_sessions:
                # Process is_admin value to ensure it's valid
                is_admin_value = session.is_admin
                if isinstance(is_admin_value, bool):
                    is_admin_value = 'admin' if is_admin_value else 'user'
                elif is_admin_value not in ['admin', 'user', '']:
                    is_admin_value = ''  # Default to empty string if invalid
                    logger.warning(f"Invalid is_admin value '{session.is_admin}' normalized to empty string")
                
                # Record in session history
                session_history = SessionHistory(
                    username=session.username,
                    businessId=session.businessId,
                    login_time=session.ztime,
                    logout_time=datetime.utcnow(),
                    device_info=session.device_info,
                    status="Auto Logout (Inactive)",
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    is_admin=is_admin_value  # Use normalized value
                )
                self.db.add(session_history)

                # Blacklist the tokens
                await blacklist_token(self.db, session.access_token)
                if session.refresh_token:
                    await blacklist_token(self.db, session.refresh_token)

                # Remove the session
                await self.db.delete(session)

            if inactive_sessions:
                await self.db.commit()
                logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
                
            return len(inactive_sessions)

        except Exception as e:
            logger.error(f"Error during inactive session cleanup")
            await self.db.rollback()
            # Don't raise exception during login flow
            if max_inactive_hours > 0:  # Only raise if specifically called as a standalone operation
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error cleaning up inactive sessions"
                )

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def check_login_attempts(self, username: str, ip_address: str) -> None:
        """Check if user is allowed to attempt login"""
        result = await self.db.execute(
            select(LoginAttempts).filter(LoginAttempts.username == username)
        )
        attempts = result.scalar()

        if attempts:
            if attempts.locked_until and attempts.locked_until > datetime.utcnow():
                lock_remaining = (attempts.locked_until - datetime.utcnow()).seconds
                logger.warning(f"Account {username} is locked. Remaining time: {lock_remaining} seconds")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is locked. Try again in {lock_remaining} seconds"
                )

            # Reset if lockout has expired
            if attempts.locked_until and attempts.locked_until <= datetime.utcnow():
                attempts.attempt_count = 0
                attempts.locked_until = None

    async def record_failed_attempt(self, username: str, ip_address: str) -> None:
        """Record a failed login attempt"""
        result = await self.db.execute(
            select(LoginAttempts).filter(LoginAttempts.username == username)
        )
        attempts = result.scalar()

        if attempts:
            attempts.attempt_count += 1
            attempts.attempt_time = datetime.utcnow()
            attempts.ip_address = ip_address

            if attempts.attempt_count >= MAX_LOGIN_ATTEMPTS:
                attempts.locked_until = datetime.utcnow() + timedelta(seconds=LOCKOUT_TIME_SECONDS)
                logger.warning(f"Account {username} locked due to too many failed attempts")
        else:
            attempts = LoginAttempts(
                username=username,
                attempt_count=1,
                ip_address=ip_address
            )
            self.db.add(attempts)

        await self.db.commit()

    async def reset_login_attempts(self, username: str) -> None:
        """Reset login attempts after successful login"""
        result = await self.db.execute(
            select(LoginAttempts).filter(LoginAttempts.username == username)
        )
        attempts = result.scalar()
        if attempts:
            await self.db.delete(attempts)
            await self.db.commit()

    async def user_login(self, form_data: OAuth2PasswordRequestForm, request: Request):
        if self.db is None:
            raise Exception("Database session not initialized")

        try:
            # Clean up inactive sessions before creating new one
            await self.cleanup_inactive_sessions()
            
            ip_address = request.client.host
            await self.check_login_attempts(form_data.username, ip_address)

            user = await self.db.execute(
                select(ApiUsers).filter_by(username=form_data.username)
            )
            user = user.scalars().first()

            if not user or not await self.verify_password(form_data.password, user.password):
                await self.record_failed_attempt(form_data.username, ip_address)
                logger.error(f"Failed login attempt for user {form_data.username} from IP {ip_address}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            if user.status != "active":
                logger.error(f"Login denied for inactive user {user.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User is not active"
                )

            await self.reset_login_attempts(user.username)

            # Create token data with essential claims
            token_data = {
                "username": user.username,
                "accode": user.accode,
                "status": user.status,
                "user_id": user.employeeCode,
                "is_admin": str(user.is_admin),
                "terminal": user.terminal,
                "businessId": int(user.businessId) if user.businessId is not None else None
            }

            access_token = await create_access_token(data=token_data)
            refresh_token = await create_refresh_token(data=token_data)

            device_info = json.dumps({
                "user_agent": str(request.headers.get("user-agent")),
                "ip": request.client.host,
                "login_time": datetime.utcnow().isoformat(),
                "device_id": request.headers.get("device-id", "unknown")  # Add support for device identification
            })

            # Create new session without checking for existing ones
            new_session = Logged(
                username=user.username,
                businessId=user.businessId,
                access_token=access_token,
                refresh_token=refresh_token,
                status="Logged In",
                device_info=device_info,
                is_admin=user.is_admin,  # Added is_admin field
                zutime=datetime.utcnow()
            )

            self.db.add(new_session)
            await self.db.commit()
            
            logger.info(f"Successful login for user {user.username} from {ip_address}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login"
            )

    async def user_logout(self, token: str, username: str):
        try:
            # Find the specific session that matches both username and token
            logged_user = await self.db.execute(
                select(Logged).filter_by(username=username, access_token=token)
            )
            logged_user = logged_user.scalars().first()

            if not logged_user:
                logger.error(f"Logout failed: No matching session found for user {username} with provided token")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No matching session found"
                )

            try:
                # Process is_admin value to ensure it's valid
                is_admin_value = logged_user.is_admin
                if isinstance(is_admin_value, bool):
                    is_admin_value = 'admin' if is_admin_value else 'user'
                elif is_admin_value not in ['admin', 'user', '']:
                    is_admin_value = ''  # Default to empty string if invalid
                    logger.warning(f"Invalid is_admin value '{logged_user.is_admin}' normalized to empty string")
                
                # Record the session history
                session_history = SessionHistory(
                    username=logged_user.username,
                    businessId=logged_user.businessId,
                    login_time=logged_user.ztime,
                    logout_time=datetime.utcnow(),
                    device_info=logged_user.device_info,
                    status="Completed",
                    access_token=logged_user.access_token,
                    refresh_token=logged_user.refresh_token,
                    is_admin=is_admin_value  # Use normalized value
                )
                
                self.db.add(session_history)
                
                # Blacklist only the tokens for this specific session
                await blacklist_token(self.db, logged_user.access_token)
                if logged_user.refresh_token:
                    await blacklist_token(self.db, logged_user.refresh_token)
                
                # Remove only this specific session
                await self.db.delete(logged_user)
                await self.db.commit()

                logger.info(f"User {username} logged out successfully from one device")
                return {"detail": f"User {username} logged out successfully from this device"}

            except Exception as db_error:
                logger.error(f"Database error during logout for user {username}: {str(db_error)}")
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error during logout process"
                )
                
        except Exception as e:
            logger.error(f"Logout error for {username}: {str(e)}")
            await self.db.rollback()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during logout"
            )

    async def handle_forced_logout(self, username: str, reason: str = "Forced Logout"):
        """Handle forced logout when user logs in from another device"""
        try:
            logged_user = await self.db.execute(
                select(Logged).filter_by(username=username)
            )
            logged_user = logged_user.scalars().first()

            if logged_user:
                # Process is_admin value to ensure it's valid
                is_admin_value = logged_user.is_admin
                if isinstance(is_admin_value, bool):
                    is_admin_value = 'admin' if is_admin_value else 'user'
                elif is_admin_value not in ['admin', 'user', '']:
                    is_admin_value = ''  # Default to empty string if invalid
                    logger.warning(f"Invalid is_admin value '{logged_user.is_admin}' normalized to empty string")
                
                # Create session history record
                session_history = SessionHistory(
                    username=logged_user.username,
                    businessId=logged_user.businessId,
                    login_time=logged_user.ztime,
                    logout_time=datetime.utcnow(),
                    device_info=logged_user.device_info,
                    status=reason,
                    access_token=logged_user.access_token,
                    refresh_token=logged_user.refresh_token,
                    is_admin=is_admin_value  # Use normalized value
                )
                
                self.db.add(session_history)
                await blacklist_token(self.db, logged_user.access_token)
                if logged_user.refresh_token:
                    await blacklist_token(self.db, logged_user.refresh_token)
                
                await self.db.delete(logged_user)
                await self.db.commit()
                
                logger.warning(f"Forced logout for user {username}: {reason}")
        
        except Exception as e:
            logger.error(f"Error during forced logout for {username}: {str(e)}")
            await self.db.rollback()
            raise

    async def get_user_sessions(self, username: str):
        """Get all active sessions for a user"""
        try:
            sessions = await self.db.execute(
                select(Logged).filter_by(username=username)
            )
            sessions = sessions.scalars().all()
            
            return [{

                "login_time": session.ztime,
                "last_activity": session.zutime,
                "device_info": json.loads(session.device_info) if session.device_info else {},
                "status": session.status
            } for session in sessions]
        except Exception as e:
            logger.error(f"Error fetching sessions for user {username}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching user sessions"
            )

    async def logout_all_sessions(self, username: str, except_token: str = None):
        """Logout from all sessions except the current one if specified"""
        try:
            # Get all sessions for the user
            query = select(Logged).filter_by(username=username)
            if except_token:
                query = query.filter(Logged.access_token != except_token)

            sessions = await self.db.execute(query)
            sessions = sessions.scalars().all()

            for session in sessions:
                # Process is_admin value to ensure it's valid
                is_admin_value = session.is_admin
                if isinstance(is_admin_value, bool):
                    is_admin_value = 'admin' if is_admin_value else 'user'
                elif is_admin_value not in ['admin', 'user', '']:
                    is_admin_value = ''  # Default to empty string if invalid
                    logger.warning(f"Invalid is_admin value '{session.is_admin}' normalized to empty string")
                
                # Create session history record
                session_history = SessionHistory(
                    username=session.username,
                    businessId=session.businessId,
                    login_time=session.ztime,
                    logout_time=datetime.utcnow(),
                    device_info=session.device_info,
                    status="Logged Out (All Sessions)",
                    access_token=session.access_token,
                    refresh_token=session.refresh_token,
                    is_admin=is_admin_value  # Use normalized value
                )
                self.db.add(session_history)

                # Blacklist the tokens
                await blacklist_token(self.db, session.access_token)
                if session.refresh_token:
                    await blacklist_token(self.db, session.refresh_token)

                # Remove the session
                await self.db.delete(session)

            await self.db.commit()
            return {"detail": "Successfully logged out all sessions"}

        except Exception as e:
            logger.error(f"Error during mass logout for user {username}: {str(e)}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error logging out all sessions"
            )
