# Role-Based Access Control (RBAC) Documentation

## Overview

The RBAC system provides granular permission control for the FastAPI application. It supports role-based permissions with a hybrid approach that maintains compatibility with the existing `is_admin` field while providing more detailed access control.

## Core Components

### 1. Database Models

#### Roles (`roles` table)
- `id`: Primary key
- `name`: Role name (e.g., "admin", "manager", "sales")
- `description`: Role description
- `is_default`: Whether this role is assigned to new users
- `created_at`: Timestamp

#### Permissions (`permissions` table)
- `id`: Primary key
- `name`: Human-readable name
- `codename`: Machine-readable identifier (e.g., "order.create")
- `resource`: Resource type (e.g., "orders", "customers")
- `action`: Action type (e.g., "create", "read", "update", "delete")
- `description`: Permission description

#### Relationships
- `user_role`: Maps users to roles (Many-to-Many)
- `role_permission`: Maps roles to permissions (Many-to-Many)

### 2. Default Roles

1. **Admin Role**
   - Has all permissions
   - Full system access

2. **Manager Role**
   - Most permissions except:
     - rbac.manage_roles
     - rbac.assign_permissions
     - user.delete
     - order.delete

3. **Sales Role**
   - Limited permissions:
     - order.create
     - order.view
     - customer.view
     - item.view
     - order.bulk_create

4. **Readonly Role**
   - All read permissions
   - No create/update/delete permissions

### 3. Permission Categories

1. **Orders**
   - order.create: Create new orders
   - order.view: View orders
   - order.edit: Edit existing orders
   - order.delete: Delete orders
   - order.bulk_create: Create multiple orders

2. **Customers**
   - customer.create: Create customers
   - customer.view: View customers
   - customer.edit: Edit customers
   - customer.delete: Delete customers

3. **Items**
   - item.create: Create items
   - item.view: View items
   - item.edit: Edit items
   - item.delete: Delete items

4. **Users**
   - user.create: Create users
   - user.view: View users
   - user.edit: Edit users
   - user.delete: Delete users

5. **RBAC**
   - rbac.manage_roles: Manage roles
   - rbac.assign_permissions: Assign permissions
   - rbac.assign_roles: Assign roles

## Usage

### 1. API Endpoints

```http
# Create a new permission
POST /api/v1/rbac/permissions
{
    "name": "Create Order",
    "codename": "order.create",
    "resource": "orders",
    "action": "create",
    "description": "Can create new orders"
}

# Create a new role
POST /api/v1/rbac/roles
{
    "name": "sales_manager",
    "description": "Sales team manager",
    "is_default": false
}

# Assign permission to role
POST /api/v1/rbac/roles/permissions
{
    "role_id": 1,
    "permission_id": 1
}

# Assign role to user
POST /api/v1/rbac/users/roles
{
    "username": "john_doe",
    "role_id": 1
}

# Get user permissions
GET /api/v1/rbac/users/{username}/permissions
```

### 2. Using Permissions in Routes

```python
from utils.permissions import has_permission

@router.post("/create-order")
@has_permission("order.create")  # Single permission
async def create_order():
    # ... order creation code ...

@router.delete("/delete-order")
@has_permission(["order.delete", "order.edit"])  # Multiple permissions
async def delete_order():
    # ... order deletion code ...
```

### 3. Permission Check Flow

1. When a route is accessed, the `@has_permission` decorator checks:
   - If user is admin (`is_admin = "admin"`) → grant access
   - Otherwise, check user's roles and their permissions
   - Grant access only if all required permissions are present

2. Example:
   ```python
   # User john_doe has "sales" role
   # Trying to access create_order endpoint
   @has_permission("order.create")
   async def create_order():
       # Access granted because "sales" role has "order.create" permission
   ```

## Security Notes

1. Admin users (`is_admin = "admin"`) automatically get all permissions
2. Permission checks are enforced at the API endpoint level
3. Role assignments are persisted in the database
4. All permission changes are logged for audit purposes

## Best Practices

1. Use the most specific permission required
2. Group related permissions into roles
3. Follow the principle of least privilege
4. Use meaningful permission codenames (resource.action)
5. Document custom roles and their permissions