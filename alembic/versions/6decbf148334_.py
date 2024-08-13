"""empty message

Revision ID: 6decbf148334
Revises: b96824fc6b36
Create Date: 2024-08-08 15:21:39.479187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6decbf148334'
down_revision: Union[str, None] = 'b96824fc6b36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
