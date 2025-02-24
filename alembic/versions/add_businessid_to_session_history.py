"""Add businessId to session_history table

Revision ID: add_businessid_to_session_history
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Check if column exists first to avoid errors
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('session_history')
    column_names = [col['name'] for col in columns]
    
    if 'businessId' not in column_names:
        # Add businessId column to session_history table (maintaining case sensitivity)
        op.add_column('session_history', sa.Column('businessId', sa.Integer))
        
        # Create an index for better query performance
        op.create_index(op.f('ix_session_history_businessId'), 'session_history', ['businessId'])

def downgrade():
    try:
        # Remove index first
        op.drop_index(op.f('ix_session_history_businessId'), table_name='session_history')
        
        # Remove column
        op.drop_column('session_history', 'businessId')
    except Exception:
        # Column might not exist
        pass