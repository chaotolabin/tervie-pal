"""Update goals macros from ratios to grams

Revision ID: 004_update_goals_macros_to_grams
Revises: 002_create_goals_table
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '004_update_goals_macros_to_grams'
down_revision = '002_create_goals_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old constraints using raw SQL (handles if not exists)
    op.execute(text('ALTER TABLE goals DROP CONSTRAINT IF EXISTS check_protein_ratio_range'))
    op.execute(text('ALTER TABLE goals DROP CONSTRAINT IF EXISTS check_fat_ratio_range'))
    op.execute(text('ALTER TABLE goals DROP CONSTRAINT IF EXISTS check_carb_ratio_range'))
    
    # Rename old columns to new names and change type
    op.alter_column('goals', 'protein_ratio',
               new_column_name='protein_grams',
               existing_type=sa.Numeric(3, 2),
               type_=sa.Numeric(6, 2),
               existing_nullable=True)
    
    op.alter_column('goals', 'fat_ratio',
               new_column_name='fat_grams',
               existing_type=sa.Numeric(3, 2),
               type_=sa.Numeric(6, 2),
               existing_nullable=True)
    
    op.alter_column('goals', 'carb_ratio',
               new_column_name='carb_grams',
               existing_type=sa.Numeric(3, 2),
               type_=sa.Numeric(6, 2),
               existing_nullable=True)
    
    # Add new constraints for grams (must be >= 0)
    op.create_check_constraint('check_protein_grams_positive', 'goals',
        'protein_grams IS NULL OR protein_grams >= 0')
    
    op.create_check_constraint('check_fat_grams_positive', 'goals',
        'fat_grams IS NULL OR fat_grams >= 0')
    
    op.create_check_constraint('check_carb_grams_positive', 'goals',
        'carb_grams IS NULL OR carb_grams >= 0')


def downgrade() -> None:
    # Drop new constraints
    op.drop_constraint('check_protein_grams_positive', 'goals', type_='check')
    op.drop_constraint('check_fat_grams_positive', 'goals', type_='check')
    op.drop_constraint('check_carb_grams_positive', 'goals', type_='check')
    
    # Change column types back and rename
    op.alter_column('goals', 'protein_grams',
               new_column_name='protein_ratio',
               existing_type=sa.Numeric(6, 2),
               type_=sa.Numeric(3, 2),
               existing_nullable=True)
    
    op.alter_column('goals', 'fat_grams',
               new_column_name='fat_ratio',
               existing_type=sa.Numeric(6, 2),
               type_=sa.Numeric(3, 2),
               existing_nullable=True)
    
    op.alter_column('goals', 'carb_grams',
               new_column_name='carb_ratio',
               existing_type=sa.Numeric(6, 2),
               type_=sa.Numeric(3, 2),
               existing_nullable=True)
    
    # Restore old constraints
    op.create_check_constraint('check_protein_ratio_range', 'goals',
        'protein_ratio IS NULL OR (protein_ratio >= 0 AND protein_ratio <= 1)')
    
    op.create_check_constraint('check_fat_ratio_range', 'goals',
        'fat_ratio IS NULL OR (fat_ratio >= 0 AND fat_ratio <= 1)')
    
    op.create_check_constraint('check_carb_ratio_range', 'goals',
        'carb_ratio IS NULL OR (carb_ratio >= 0 AND carb_ratio <= 1)')
