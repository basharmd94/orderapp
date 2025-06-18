# HMBR Mobile Apps API Documentation

## Overview

HMBR Mobile Apps API is an enterprise-grade API built with FastAPI for Mobile Order Apps serving HMBR, GI Corporation & Zepto Chemicals. This application handles order processing, inventory management, user authentication, and customer relationship management with a microservice architecture.

## Tech Stack

- **Backend**: FastAPI, Pydantic, SQLAlchemy (Async), PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Database Migrations**: Alembic
- **Frontend**: 
  - Admin Dashboard: React with Material UI
  - Mobile App: React Native with Expo

## Project Structure

```
orderapp/
├── alembic/                # Database migration scripts
├── app/                    # Main application code
│   ├── controllers/        # Business logic controllers
│   │   └── db_controllers/ # Database interaction controllers
│   ├── dependencies/       # FastAPI dependencies
│   ├── models/             # SQLAlchemy models (database tables)
│   ├── routers/            # API endpoints (route handlers)
│   ├── schemas/            # Pydantic models for validation
│   ├── utils/              # Utility functions
│   ├── database.py         # Database connection setup
│   ├── logs.py             # Logging configuration
│   └── main.py             # Application entry point
├── adminflow/              # Admin dashboard frontend
└── mobileapp/              # Mobile app frontend
```

## Features

### Users
- User authentication using JWT tokens
- Refresh token mechanism for maintaining sessions
- Role-based access control system
- User profile management
- Session tracking and management

### Orders
- Create single and bulk orders
- Asynchronous order processing with worker tasks
- Order status tracking
- Order history and analytics

### Items
- Inventory management
- Stock tracking
- Price management with discount support

### Customers
- Customer management
- Customer history
- Analytics and reporting

## Database Schema

### User Management Tables
- **ApiUsers**: Core user table storing authentication credentials and user information
  - Fields: id, username, password, employee_name, email, mobile, businessId, employeeCode, terminal, is_admin, status, accode
- **Logged**: Tracks active login sessions
  - Fields: id, ztime, zutime, username, businessId, access_token, refresh_token, status, device_info, is_admin
- **SessionHistory**: Records historical login sessions
  - Fields: id, username, businessId, login_time, logout_time, device_info, status, access_token, refresh_token, is_admin
- **TokenBlacklist**: Stores invalidated tokens for security
  - Fields: id, token, blacklisted_at
- **LoginAttempts**: Tracks failed login attempts for security
  - Fields: id, username, attempt_time, attempt_count, locked_until, ip_address

### RBAC (Role-Based Access Control) Tables
- **roles**: Defines user roles in the system
  - Fields: id, name, description, is_default, created_at
- **permissions**: Defines granular permissions for actions
  - Fields: id, name, codename, description, resource, action
- **role_permission**: Many-to-many relationship between roles and permissions
  - Fields: role_id, permission_id
- **user_role**: Many-to-many relationship between users and roles
  - Fields: username, role_id

### Order Management Tables
- **Opmob**: Mobile order items with detailed information
  - Fields: invoicesl, xroword, zutime, xdate, xqty, xlat, xlong, xlinetotal, xtra1, xtra2, xprice, ztime, zid, xtra3, xtra4, xtra5, invoiceno, username, xemp, xcus, xcusname, xcusadd, xitem, xdesc, xstatusord, xordernum, xterminal, xsl
- **Opord**: Order header information
  - Fields: zid, xordernum, xdate

### Inventory Tables
- **Caitem**: Product catalog information
  - Fields: zid, xitem, xdesc, xgitem, xstdprice, xunitstk, xbin
- **Imtrn**: Inventory movement transactions
  - Fields: zid, xitem, xqty, xsign
- **Opspprc**: Special pricing information
  - Fields: zid, xpricecat, xqty, xdisc
- **FinalItemsView**: Materialized view combining inventory data for improved performance
  - Fields: zid, item_id, item_name, item_group, std_price, stock, min_disc_qty, disc_amt, xbin
  - SQL Definition:
    ```sql
   DROP MATERIALIZED VIEW IF EXISTS final_items_view;

  CREATE MATERIALIZED VIEW final_items_view AS
  SELECT
      ci.zid,
      ci.xitem AS item_id,
      ci.xdesc AS item_name,
      ci.xgitem AS item_group,
      ci.xstdprice AS std_price,
      ci.xunitstk AS stock_unit,
      ci.xbin AS xbin,
      ts.stock,
      COALESCE(MIN(op.xqty), 0) AS min_disc_qty,
      COALESCE(MIN(op.xdisc), 0) AS disc_amt
  FROM
      caitem ci
  JOIN
      (
          SELECT
              im.zid,
              im.xitem,
              im.xwh,
              SUM(im.xqty * im.xsign) AS stock
          FROM
              imtrn im
          WHERE
              (im.zid = 100001 AND im.xwh = 'HMBR -Main Store (4th Floor)')
              OR (im.zid = 100000 AND im.xwh = 'Sales Warehouse GI')
              OR (im.zid = 100005 AND im.xwh = 'Sales Warehouse(Zepto)')
          GROUP BY
              im.zid, im.xitem, im.xwh
      ) ts
  ON
      ci.xitem = ts.xitem
      AND ci.zid = ts.zid
  LEFT JOIN
      opspprc op
  ON
      ci.xitem = op.xpricecat
      AND ci.zid = op.zid
  GROUP BY
      ci.zid,
      ci.xitem,
      ci.xdesc,
      ci.xgitem,
      ci.xstdprice,
      ci.xunitstk,
      ci.xbin,
      ts.stock;
    ```
  - Refresh Command:
    ```sql
    REFRESH MATERIALIZED VIEW final_items_view;
    ```
  - Daily scheduled refresh via script `H_77_sync_items`


### Location Tracking Table

To create the location_records table for location tracking, run the following SQL:

```sql
CREATE TABLE location_records (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    altitude FLOAT,
    accuracy FLOAT,
    name VARCHAR(255),
    street VARCHAR(255),
    district VARCHAR(255),
    city VARCHAR(255),
    region VARCHAR(255),
    postal_code VARCHAR(50),
    country VARCHAR(100),
    formatted_address TEXT,
    maps_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP NOT NULL,
    xdate VARCHAR(10),
    business_id INTEGER,
    notes TEXT,
    device_info VARCHAR(255),
    is_check_in BOOLEAN DEFAULT FALSE,
    shared_via VARCHAR(100)
);

-- Add indexes for efficient querying
CREATE INDEX idx_location_username ON location_records(username);
CREATE INDEX idx_location_timestamp ON location_records(timestamp);
CREATE INDEX idx_location_business_id ON location_records(business_id);
```

### Feedback Tables query

```sql
  -- Create the main feedback table
  -- Create the simplified feedback table
CREATE TABLE feedback (
    id SERIAL,
    zid INTEGER NOT NULL,
    customer_id VARCHAR NOT NULL,
    product_id VARCHAR NOT NULL,
    is_delivery_issue BOOLEAN DEFAULT FALSE,
    is_collection_issue BOOLEAN DEFAULT FALSE,
    description TEXT NOT NULL,
    translated_desc TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(50) REFERENCES "apiUsers"(username),
    user_id VARCHAR(50),
    PRIMARY KEY (id, zid)
     );

```


### Customer Tables
- **Cacus**: Customer information
  - Fields: zid, xcus, xorg, xadd1, xcity, xstate, xmobile, xtaxnum, xsp, xsp1, xsp2, xsp3

### Employee Tables
- **Prmst**: Employee information
  - Fields: zid, xemp, xname, xproj, xstatusemp

## API Endpoints

The API is organized under `/api/v1/` with the following main route groups:

- `/api/v1/users`: User authentication and management
- `/api/v1/items`: Inventory and product management
- `/api/v1/customers`: Customer data management
- `/api/v1/order`: Order processing and tracking
- `/api/v1/rbac`: Role-based access control
- `/api/v1/admin`: Administrative operations
- `/api/v1/health`: System health monitoring

## Authentication

All API endpoints are protected with JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

The authentication flow includes:
- Login process that returns access and refresh tokens
- Token validation on each request
- Token refreshing mechanism
- Session tracking and automatic expiry

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Node.js and npm (for frontend)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=<generated_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/da
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_TIME_SECONDS=300
```

You can generate a secure SECRET_KEY using the included utility:

```bash
python generate_secret.py
```

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd orderapp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI application:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Admin Dashboard Setup

```bash
cd adminflow
npm install
npm start
```

### Mobile App Setup

```bash
cd mobileapp
npm install
npx expo start
```

## Development

### Creating Database Migrations

After modifying models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### API Documentation

The API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI Schema: `/openapi.json`

## Deployment

The application is designed to be deployed in a variety of environments:

1. Standard server deployment with uvicorn
2. Docker containerization
3. Cloud service deployment (AWS, Azure, GCP)

For production deployment, ensure:
1. Set appropriate environment variables
2. Use a production-grade database connection
3. Use proper logging and monitoring
4. Set up appropriate CORS configuration

## Troubleshooting

Common issues:

1. **Database connection errors**: Check your PostgreSQL service is running and DATABASE_URL is correct
2. **Authentication issues**: Verify SECRET_KEY is set correctly and tokens are valid
3. **Application restart loops**: Check the lifespan function in main.py, especially database connection disposal
4. **High resource usage**: Monitor worker tasks and database connections to prevent leaks

## RBAC (Role-Based Access Control)

The system implements a comprehensive RBAC system that controls access to various API endpoints based on user roles and permissions. See `/app/docs/rbac_documentation.md` for details.

## Contact

For any questions or support, contact:
- **Name**: Bashar
- **Email**: mat197194@gmail.com
- **Website**: https://bashar.pythonanywhere.com/

## License

This project is licensed under the MIT License - see the LICENSE file for details.
