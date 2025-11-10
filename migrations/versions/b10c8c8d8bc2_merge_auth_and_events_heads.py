"""merge auth and events heads

Revision ID: b10c8c8d8bc2
Revises: 20251105_000002, 4fbfbbb0f7af
Create Date: 2025-11-07 16:36:06.632495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b10c8c8d8bc2'
down_revision: Union[str, Sequence[str], None] = ('20251105_000002', '4fbfbbb0f7af')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
