from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from typing import List
import logging
import os
from dotenv import load_dotenv
import json
from sqlalchemy import inspect
from contextlib import asynccontextmanager

# Local imports
from routers import (
    opord_route,
    items_route,
    users_route,
    customers_route,
    orders_route,
    rbac_route,
    user_manage_route,
    customer_balance_route,  # Add customer balance route
    location_route,  # Add location route
    feedback_route,  # Add feedback route
)

from database import engine, Base, get_db, async_session_maker
from logs import setup_logger
from utils.auth import session_activity_middleware

# Configure logging
logger = setup_logger()

# Load environment variables
load_dotenv()

def validate_env_vars():
    # Required environment variables with their validation functions
    required_env_vars = {
        "SECRET_KEY": lambda x: len(x) >= 32,  # At least 32 chars for security
        "ALGORITHM": lambda x: x in ["HS256", "HS384", "HS512"],  # Only allow HMAC-SHA algorithms
        "ACCESS_TOKEN_EXPIRE_MINUTES": lambda x: x.isdigit() and 60 <= int(x) <= 120,  # Between 5-60 minutes
        "REFRESH_TOKEN_EXPIRE_DAYS": lambda x: x.isdigit() and 1 <= int(x) <= 30,  # Between 1-30 days
        "DATABASE_URL": lambda x: "postgresql" in x,  # Simplified validation for database URL
        "MAX_LOGIN_ATTEMPTS": lambda x: x.isdigit() and 1 <= int(x) <= 10,
        "LOCKOUT_TIME_SECONDS": lambda x: x.isdigit() and 60 <= int(x) <= 3600,
    }
    
    missing_vars = []
    invalid_vars = []

    for var_name, validator in required_env_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(var_name)
            continue
        
        # Special handling for database URL to handle escape characters
        if var_name == "DATABASE_URL":
            # Handle various escape sequences
            escape_chars = {
                '\\x3a': ':',
                '\\x40': '@',
                '\\x2f': '/',
                '\\x3f': '?',
                '\\x3d': '=',
                '\\x26': '&',
            }
            
            fixed_value = value
            for escape_seq, char in escape_chars.items():
                if escape_seq in fixed_value:
                    fixed_value = fixed_value.replace(escape_seq, char)
                    logger.info(f"Replaced escape sequence {escape_seq} with {char} in DATABASE_URL")
            
            if fixed_value != value:
                logger.info(f"Fixed DATABASE_URL: {fixed_value}")
                os.environ[var_name] = fixed_value
                value = fixed_value
        
        if not validator(value):
            invalid_vars.append(f"{var_name}={value}")
    
    if missing_vars:
        raise ValueError(f"Required environment variables not set: {', '.join(missing_vars)}")
    if invalid_vars:
        raise ValueError(f"Invalid environment variable values: {', '.join(invalid_vars)}")

    logger.info("Environment variables validated successfully")

# Validate environment variables at startup
validate_env_vars()

# API Metadata
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

description = """
# HMBR Mobile Apps API

Enterprise-grade API for Mobile Order Apps serving HMBR, GI Corporation & Zepto Chemicals. 🚀

## Features

### Users
* User authentication and authorization
* User profile management
* Role-based access control

### Orders
* Create single and bulk orders
* Track order status
* Order history and analytics

### Items
* Inventory management
* Stock tracking
* Price management

### Customers
* Customer management
* Customer history
* Analytics and reporting

## Authentication
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```
"""

tags_metadata = [
    {
        "name": "Users",
        "description": "User management operations including authentication and profile management.",
    },
    {
        "name": "Orders",
        "description": "Order management including creation, tracking, and history.",
    },
    {
        "name": "Items",
        "description": "Inventory and stock management operations.",
    },
    {
        "name": "Customers",
        "description": "Customer relationship management operations.",
    },
    {
        "name": "Location",
        "description": "User location tracking and geolocation management.",
    },
    {
        "name": "Feedback",
        "description": "Customer feedback management including delivery and collection issues.",
    },
]

# Function to create tables asynchronously
async def create_database():
    """Create all tables in the database asynchronously if they don't already exist."""
    async with engine.begin() as conn:
        # Use conn.run_sync to run synchronous inspection logic
        existing_tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        if not existing_tables:  # Only create tables if none exist
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    try:
        logger.info("Starting up application...")
        await create_database()
        logger.info("Database tables created successfully.")
        yield  # Application runs here
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        try:
            logger.info("Shutting down application...")
            await engine.dispose()
            logger.info("Application shutdown completed.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="HMBR Mobile Apps API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Bashar",
        "url": "https://bashar.pythonanywhere.com/",
        "email": "mat197194@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Import test routes only in debug mode
try:
    from routers import test_route, test_post_route
    has_test_routes = True
except ImportError:
    has_test_routes = False
    logger.warning("Test routes not available")

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:8050",
    "http://localhost:8000",
    "*",  # Allow all origins (not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session activity middleware with database dependency
@app.middleware("http")
async def add_db_to_request(request: Request, call_next):
    # Create a new session from the existing engine pool
    async with async_session_maker() as db:
        request.state.db = db
        try:
            response = await call_next(request)
            return response
        finally:
            # Ensure session is closed properly
            await db.close()

# Add session activity middleware after database middleware
@app.middleware("http")
async def activity_middleware(request: Request, call_next):
    return await session_activity_middleware(request, call_next)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )

@app.middleware("http")
async def debug_request_middleware(request: Request, call_next):
    # Log request details
    logger.debug(f"Request path: {request.url.path}")
    logger.debug(f"Request method: {request.method}")
    
    # Only log request body for specific endpoints that might handle is_admin
    if request.url.path.endswith(("/login", "/logout", "/registration")):
        try:
            body = await request.body()
            if body:
                body_str = body.decode()
                logger.debug(f"Request body: {body_str}")
                # Check for boolean values in the request
                if '"is_admin":' in body_str and ('true' in body_str.lower() or 'false' in body_str.lower()):
                    logger.warning(f"Found boolean is_admin in request body for {request.url.path}")
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")

    response = await call_next(request)

    # Log response details for errors
    if response.status_code >= 400:
        logger.error(f"Error response status: {response.status_code}")
        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            logger.error(f"Error response body: {response_body.decode()}")
            # Reconstruct response since we consumed the body iterator
            return Response(content=response_body, status_code=response.status_code, 
                          headers=dict(response.headers))
        except Exception as e:
            logger.error(f"Error reading response body: {str(e)}")

    return response

# Health check endpoint
@app.get(
    f"{API_PREFIX}/health",
    tags=["System"],
    summary="System health check",
    response_model=dict,
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    Perform a health check of the system.
    Returns:
        dict: Health status of the system
    """
    return {
        "status": "healthy",
        "version": app.version,
        "api_version": API_VERSION
    }

# Router configuration
router_configs = [
    {
        "router": items_route.router,
        "prefix": f"{API_PREFIX}/items",
        "tags": ["Items"],
        "responses": {404: {"description": "Item not found"}},
    },
    {
        "router": users_route.router,
        "prefix": f"{API_PREFIX}/users",
        "tags": ["Users"],
        "responses": {401: {"description": "Unauthorized"}},
    },
    {
        "router": customers_route.router,
        "prefix": f"{API_PREFIX}/customers",
        "tags": ["Customers"],
        "responses": {404: {"description": "Customer not found"}},
    },
    {
        "router": orders_route.router,
        "prefix": f"{API_PREFIX}/order",
        "tags": ["Orders"],
        "responses": {400: {"description": "Invalid order data"}},
    },
    {
        "router": rbac_route.router,
        "prefix": f"{API_PREFIX}/rbac",
        "tags": ["RBAC"],
        "responses": {403: {"description": "Insufficient permissions"}},
    },
    {
        "router": customer_balance_route.router,
        "prefix": f"{API_PREFIX}/customer-balance",
        "tags": ["Customer Balance"],
        "responses": {404: {"description": "Customer balance data not found"}},
    },
    {
        "router": location_route.router,
        "prefix": f"{API_PREFIX}/location",
        "tags": ["Location"],
        "responses": {404: {"description": "Location data not found"}},
    },
    {
        "router": feedback_route.router,
        "prefix": f"{API_PREFIX}/feedback",
        "tags": ["Feedback"],
        "responses": {404: {"description": "Feedback data not found"}},
    },
]

# Include all routers
for config in router_configs:
    app.include_router(**config)

app.include_router(user_manage_route.router, prefix="/api/v1/admin", tags=["User Management"])  # Add this line

# Development routes (should be disabled in production)
if app.debug and has_test_routes:
    app.include_router(
        test_route.router,
        prefix=f"{API_PREFIX}/test",
        tags=["Development"],
    )
    app.include_router(
        test_post_route.router,
        prefix=f"{API_PREFIX}/testpost",
        tags=["Development"],
    )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that redirects users to the API documentation
    """
    return {
        "message": "Welcome to HMBR Mobile Apps API",
        "documentation": "/docs",
        "redoc": "/redoc",
        "version": app.version,
        "api_version": API_VERSION,
        "contact": {
            "name": "Bashar",
            "url": "https://bashar.pythonanywhere.com/",
            "email": "mat197194@gmail.com",
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
            },
        "status": "healthy",
        "tags": [tag["name"] for tag in tags_metadata]

    }

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8500,
        reload=True,
        workers=4,  # Increased to 4 workers with PostgreSQL max_connections=800
        log_level="info"
    )
