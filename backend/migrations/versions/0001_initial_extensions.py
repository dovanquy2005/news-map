"""Enable initial database extensions: uuid-ossp, postgis, and vector.

Revision ID: 0001_initial_extensions
Revises: 
Create Date: 2026-09-20 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_extensions"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. UUID generation extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # 2. Mandatory PostGIS spatial extension (ADR-002)
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis";')

    # 3. Vector search extension for embedding similarity (optional/future proof)
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector";')


def downgrade() -> None:
    # Drop in reverse order with safety check
    op.execute('DROP EXTENSION IF EXISTS "vector";')
    op.execute('DROP EXTENSION IF EXISTS "postgis";')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
