import traceback
from fastapi import HTTPException, status, Form, Request
from controllers.db_controllers.database_controller import DatabaseController
from models.users_model import ApiUsers, Logged, TokenBlacklist, SessionHistory, LoginAttempts
from fastapi.security import OAuth2PasswordRequestForm
from utils.error import error_details
from utils.auth import (
    create_access_token, 
    create_refresh_token, 
    verify_password, 
    blacklist_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM
)
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

logger = setup_logger()

class UserLoginController:
    def __init__(self, db: AsyncSession):
        self.db = db

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
            ip_address = request.client.host
            await self.check_login_attempts(form_data.username, ip_address)

            user = await self.db.execute(
                select(ApiUsers).filter_by(username=form_data.username)
            )
            user = user.scalars().first()

            if not user or not await verify_password(form_data.password, user.password):
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

            existing_session = await self.db.execute(
                select(Logged).filter_by(username=user.username)
            )
            existing_session = existing_session.scalars().first()

            if existing_session:
                logger.info(f"Forcing logout of previous session for user {user.username}")
                await blacklist_token(self.db, existing_session.access_token)
                if existing_session.refresh_token:
                    await blacklist_token(self.db, existing_session.refresh_token)
                await self.db.delete(existing_session)
                await self.db.commit()

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
                "login_time": datetime.utcnow().isoformat()
            })

            new_session = Logged(
                username=user.username,
                businessId=user.businessId,
                access_token=access_token,
                refresh_token=refresh_token,
                status="Logged In",
                device_info=device_info,
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
            logged_user = await self.db.execute(
                select(Logged).filter_by(username=username)
            )
            logged_user = logged_user.scalars().first()

            if not logged_user:
                logger.error(f"Logout failed: No active session for user {username}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active session found"
                )

            try:
                with self.db.no_autoflush:
                    user_query = await self.db.execute(
                        select(ApiUsers).filter_by(username=username)
                    )
                    user = user_query.scalar()
                    
                    if not user:
                        logger.warning(f"User record not found during logout - username: {username}")

                    session_history = SessionHistory(
                        username=logged_user.username,
                        businessId=logged_user.businessId,
                        login_time=logged_user.ztime,
                        logout_time=datetime.utcnow(),
                        device_info=logged_user.device_info,
                        status="Completed",
                        access_token=logged_user.access_token,
                        refresh_token=logged_user.refresh_token,
                        is_admin=user.is_admin if user else "user"
                    )
                    
                    self.db.add(session_history)
                    await blacklist_token(self.db, logged_user.access_token)
                    if logged_user.refresh_token:
                        await blacklist_token(self.db, logged_user.refresh_token)
                    
                    await self.db.delete(logged_user)
                    await self.db.commit()

                    logger.info(f"User {username} logged out successfully")
                    return {"detail": f"User {username} logged out successfully"}

            except Exception as db_error:
                logger.error(f"Database error during logout for user {username}: {str(db_error)}")
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
                detail=f"An error occurred during logout"
            )

    async def handle_forced_logout(self, username: str, reason: str = "Forced Logout"):
        """Handle forced logout when user logs in from another device"""
        try:
            logged_user = await self.db.execute(
                select(Logged).filter_by(username=username)
            )
            logged_user = logged_user.scalars().first()

            if logged_user:
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
                    is_admin= logged_user.is_admin  # Set default value
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
