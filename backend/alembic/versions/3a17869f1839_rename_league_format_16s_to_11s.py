"""rename league format 16s to 11s

Revision ID: 3a17869f1839
Revises: a2099e8c30bd
Create Date: 2026-11-04 18:22:41.873147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a17869f1839'
down_revision: Union[str, Sequence[str], None] = 'a2099e8c30bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE league_format RENAME VALUE 'SIXTEENS' TO 'ELEVENS'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE league_format RENAME VALUE 'ELEVENS' TO 'SIXTEENS'")

