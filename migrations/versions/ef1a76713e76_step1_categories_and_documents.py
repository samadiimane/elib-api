"""step1: categories and documents

Revision ID: ef1a76713e76
Revises: 37b5e759b138
Create Date: 2025-10-16 12:26:13.212189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef1a76713e76'
down_revision: Union[str, Sequence[str], None] = '37b5e759b138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
