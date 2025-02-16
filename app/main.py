from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
import logging

# Local imports
from routers import (
    opord_route,
    items_route,
    users_route,
    customers_route,
    orders_route,
    test_route,
    test_post_route 
)
from database import engine, Base
from logs import setup_logger

# Configure logging
logger = setup_logger()

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
]

# Initialize FastAPI app
app = FastAPI(
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
]

# Include all routers
for config in router_configs:
    app.include_router(**config)

# Development routes (should be disabled in production)
if app.debug:
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

# Function to create tables asynchronously
async def create_database():
    """Create all tables in the database asynchronously.

    This function creates all tables in the database using the metadata
    defined in the Base class. It is an asynchronous function and should be
    used with the `asyncio` library.

    Example:
        async def main():
            await create_database()

        asyncio.run(main())
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_database()

@app.on_event("shutdown")
async def shutdown_event():
    """Execute shutdown tasks."""
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Application shutdown completed")

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
        port=8050,
        reload=True,
        workers=4,
        log_level="info"
    )


