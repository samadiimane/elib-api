"""step1.5: rename legacy tables and clean model exports

Revision ID: 02440c4b7c1e
Revises: 0af65fca626a
Create Date: 2025-10-16 13:20:14.675645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02440c4b7c1e'
down_revision: Union[str, Sequence[str], None] = '0af65fca626a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
