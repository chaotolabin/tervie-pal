"""Create support_tickets table

Revision ID: 002_create_support_tables
Revises: b48d94ac46c3
Create Date: 2026-01-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_create_support_tables'
down_revision = 'b48d94ac46c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    # op.execute("CREATE TYPE ticket_status_enum AS ENUM ('open', 'in_progress', 'resolved', 'closed')")
    # op.execute("CREATE TYPE ticket_category_enum AS ENUM ('bug', 'feature_request', 'question', 'other')")
    
    # Create support_tickets table
    op.create_table(
        'support_tickets',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='ID ticket'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, comment='FK tới users.id (NULL nếu guest)'),
        sa.Column('subject', sa.Text(), nullable=False, comment='Tiêu đề ticket'),
        sa.Column('message', sa.Text(), nullable=False, comment='Nội dung chi tiết'),
        sa.Column('category', sa.Enum('bug', 'feature_request', 'question', 'other', name='ticket_category_enum'), nullable=True, comment='Phân loại ticket'),
        sa.Column('status', sa.Enum('open', 'in_progress', 'resolved', 'closed', name='ticket_status_enum'), nullable=False, server_default='open', comment='Trạng thái xử lý'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_support_ticket_status', 'support_tickets', ['status'])
    op.create_index('ix_support_ticket_category', 'support_tickets', ['category'])
    op.create_index('ix_support_ticket_user_id', 'support_tickets', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_support_ticket_user_id', table_name='support_tickets')
    op.drop_index('ix_support_ticket_category', table_name='support_tickets')
    op.drop_index('ix_support_ticket_status', table_name='support_tickets')
    
    # Drop table
    op.drop_table('support_tickets')
    
    # Drop ENUM types
    op.execute('DROP TYPE ticket_category_enum')
    op.execute('DROP TYPE ticket_status_enum')