"""Add is_banned to users tables

Revision ID: f8c58df761ee
Revises: b96824fc6b36
Create Date: 2024-08-11 17:34:09.395775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8c58df761ee'
down_revision: Union[str, None] = 'c556d3180c82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tg_users', sa.Column('is_banned', sa.Numeric(), nullable=True))
    op.add_column('vk_users', sa.Column('is_banned', sa.Numeric(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('vk_users', 'is_banned')
    op.drop_column('tg_users', 'is_banned')
    # ### end Alembic commands ###
