"""Create goals table

Revision ID: 002_create_goals_table
Revises: 001_create_auth_tables
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '002_create_goals_table'
down_revision = '001_create_auth_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('goal_type', sa.Text(), nullable=False),
        sa.Column('target_weight_kg', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('daily_calorie_target', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column('protein_ratio', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('fat_ratio', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('carb_ratio', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('weekly_exercise_min', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('goals')