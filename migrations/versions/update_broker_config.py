"""Update broker config model

Revision ID: 1234abcd5678
Revises: previous_revision_id
Create Date: 2024-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '1234abcd5678'
down_revision = None  # Change this to your previous migration if exists
branch_labels = None
depends_on = None

def upgrade():
    # Drop old columns if they exist
    with op.batch_alter_table('broker_config') as batch_op:
        batch_op.drop_column('api_key')
        batch_op.drop_column('api_secret')
        batch_op.drop_column('account_id')
        
        # Add new columns
        batch_op.add_column(sa.Column('oanda_api_key', sa.String(255)))
        batch_op.add_column(sa.Column('oanda_account_id', sa.String(50)))
        batch_op.add_column(sa.Column('oanda_environment', sa.String(20), server_default='practice'))
        batch_op.add_column(sa.Column('alpaca_api_key', sa.String(255)))
        batch_op.add_column(sa.Column('alpaca_api_secret', sa.String(255)))
        batch_op.add_column(sa.Column('alpaca_paper_trading', sa.Boolean(), server_default='1'))
        batch_op.add_column(sa.Column('supported_markets', sa.JSON))

def downgrade():
    # Revert changes if needed
    with op.batch_alter_table('broker_config') as batch_op:
        batch_op.drop_column('oanda_api_key')
        batch_op.drop_column('oanda_account_id')
        batch_op.drop_column('oanda_environment')
        batch_op.drop_column('alpaca_api_key')
        batch_op.drop_column('alpaca_api_secret')
        batch_op.drop_column('alpaca_paper_trading')
        batch_op.drop_column('supported_markets')
        
        # Restore original columns
        batch_op.add_column(sa.Column('api_key', sa.String(255)))
        batch_op.add_column(sa.Column('api_secret', sa.String(255)))
        batch_op.add_column(sa.Column('account_id', sa.String(50)))
