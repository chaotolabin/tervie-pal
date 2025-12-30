"""Create users, profiles, and refresh_sessions tables

Revision ID: 001_create_auth_tables
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '001_create_auth_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old ENUM types and tables if they exist (clean slate)
    op.execute(text("DROP TABLE IF EXISTS refresh_sessions CASCADE;"))
    op.execute(text("DROP TABLE IF EXISTS profiles CASCADE;"))
    op.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    op.execute(text("DROP TYPE IF EXISTS user_role_enum CASCADE;"))
    op.execute(text("DROP TYPE IF EXISTS gender_enum CASCADE;"))
    
    # Create ENUM types
    op.execute(text("CREATE TYPE user_role_enum AS ENUM ('user', 'admin');"))
    op.execute(text("CREATE TYPE gender_enum AS ENUM ('male', 'female');"))
    
    # Create users table using raw SQL
    op.execute(text("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role user_role_enum NOT NULL DEFAULT 'user',
            password_changed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """))
    
    # Create profiles table using raw SQL
    op.execute(text("""
        CREATE TABLE profiles (
            user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            full_name TEXT,
            gender gender_enum,
            date_of_birth DATE,
            height_cm_default FLOAT CHECK (height_cm_default IS NULL OR height_cm_default > 0),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """))
    
    # Create refresh_sessions table using raw SQL
    op.execute(text("""
        CREATE TABLE refresh_sessions (
            id BIGSERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            refresh_token_hash TEXT NOT NULL UNIQUE,
            device_label TEXT,
            user_agent TEXT,
            ip INET,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            last_used_at TIMESTAMP WITH TIME ZONE,
            revoked_at TIMESTAMP WITH TIME ZONE
        );
    """))
    
    # Create indexes
    op.execute(text("""
        CREATE INDEX ix_refresh_sessions_user_id ON refresh_sessions(user_id) 
        WHERE revoked_at IS NULL;
    """))


def downgrade() -> None:
    # Drop tables
    op.drop_table('refresh_sessions')
    op.drop_table('profiles')
    op.drop_table('users')
    
    # Drop ENUM types
    op.execute(text("DROP TYPE IF EXISTS user_role_enum CASCADE;"))
    op.execute(text("DROP TYPE IF EXISTS gender_enum CASCADE;"))
