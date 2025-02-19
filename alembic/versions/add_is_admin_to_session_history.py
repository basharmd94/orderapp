"""Add is_admin to session_history table

Revision ID: add_is_admin_to_session_history
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Check if column exists first to avoid errors
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('session_history')
    column_names = [col['name'] for col in columns]
    
    if 'is_admin' not in column_names:
        # Add is_admin column to session_history table
        op.add_column('session_history', sa.Column('is_admin', sa.String))

def downgrade():
    try:
        # Remove column
        op.drop_column('session_history', 'is_admin')
    except Exception:
        # Column might not exist
        pass