"""add_rbac_tables

Revision ID: rbac_system
Revises: add_is_admin_to_session_history
Create Date: 2023-09-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'rbac_system'
down_revision = 'add_is_admin_to_session_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('created_at', sa.Integer(), server_default=sa.text(str(int(datetime.now().timestamp())))),
    )
    
    # Create the permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('codename', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
    )
    
    # Create the many-to-many relationship table between roles and permissions
    op.create_table(
        'role_permission',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE')),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id', ondelete='CASCADE')),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )
    
    # Create the many-to-many relationship table between users and roles
    op.create_table(
        'user_role',
        sa.Column('user_id', sa.String(50), sa.ForeignKey('apiUsers.employeeCode', ondelete='CASCADE')),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete='CASCADE')),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
    )
    
    # Create predefined roles and permissions
    op.execute("""
    -- Insert default roles
    INSERT INTO roles (name, description, is_default) VALUES 
    ('admin', 'System administrator with full access', false),
    ('manager', 'Manager with access to most features', false),
    ('sales', 'Sales staff with limited access', true),
    ('readonly', 'Read-only access to data', false);
    
    -- Insert permissions
    INSERT INTO permissions (name, codename, description, resource, action) VALUES
    -- Orders permissions
    ('Create Order', 'order.create', 'Can create new orders', 'orders', 'create'),
    ('View Orders', 'order.view', 'Can view orders', 'orders', 'read'),
    ('Edit Orders', 'order.edit', 'Can edit existing orders', 'orders', 'update'),
    ('Delete Orders', 'order.delete', 'Can delete orders', 'orders', 'delete'),
    ('Bulk Create Orders', 'order.bulk_create', 'Can create multiple orders at once', 'orders', 'bulk_create'),
    
    -- Customers permissions
    ('Create Customer', 'customer.create', 'Can create new customers', 'customers', 'create'),
    ('View Customers', 'customer.view', 'Can view customers', 'customers', 'read'),
    ('Edit Customers', 'customer.edit', 'Can edit existing customers', 'customers', 'update'),
    ('Delete Customers', 'customer.delete', 'Can delete customers', 'customers', 'delete'),
    
    -- Items permissions
    ('Create Item', 'item.create', 'Can create new items', 'items', 'create'),
    ('View Items', 'item.view', 'Can view items', 'items', 'read'),
    ('Edit Items', 'item.edit', 'Can edit existing items', 'items', 'update'),
    ('Delete Items', 'item.delete', 'Can delete items', 'items', 'delete'),
    
    -- User permissions
    ('Create User', 'user.create', 'Can create users', 'users', 'create'),
    ('View Users', 'user.view', 'Can view user information', 'users', 'read'),
    ('Edit Users', 'user.edit', 'Can edit user information', 'users', 'update'),
    ('Delete Users', 'user.delete', 'Can delete users', 'users', 'delete'),
    
    -- RBAC permissions
    ('Manage Roles', 'rbac.manage_roles', 'Can manage roles', 'rbac', 'manage'),
    ('Assign Permissions', 'rbac.assign_permissions', 'Can assign permissions to roles', 'rbac', 'assign'),
    ('Assign Roles', 'rbac.assign_roles', 'Can assign roles to users', 'rbac', 'assign');
    """)
    
    # Assign permissions to roles
    op.execute("""
    -- Assign permissions to admin role
    INSERT INTO role_permission (role_id, permission_id)
    SELECT 1, id FROM permissions;
    
    -- Assign permissions to manager role
    INSERT INTO role_permission (role_id, permission_id)
    SELECT 2, id FROM permissions WHERE codename NOT IN ('rbac.manage_roles', 'rbac.assign_permissions', 'user.delete', 'order.delete');
    
    -- Assign permissions to sales role
    INSERT INTO role_permission (role_id, permission_id)
    SELECT 3, id FROM permissions WHERE codename IN ('order.create', 'order.view', 'customer.view', 'item.view', 'order.bulk_create');
    
    -- Assign permissions to readonly role
    INSERT INTO role_permission (role_id, permission_id)
    SELECT 4, id FROM permissions WHERE action = 'read';
    """)


def downgrade() -> None:
    op.drop_table('user_role')
    op.drop_table('role_permission')
    op.drop_table('permissions')
    op.drop_table('roles')