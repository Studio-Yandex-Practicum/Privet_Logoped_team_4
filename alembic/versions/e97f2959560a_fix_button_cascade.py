"""Fix Button CASCADE

Revision ID: e97f2959560a
Revises: 7c805d8a5bd8
Create Date: 2024-08-12 15:37:18.597064

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e97f2959560a'
down_revision: Union[str, None] = '7c805d8a5bd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('buttons_parent_button_id_fkey', 'buttons', type_='foreignkey')
    op.create_foreign_key('parent_id', 'buttons', 'buttons', ['parent_button_id'], ['button_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('parent_id', 'buttons', type_='foreignkey')
    op.create_foreign_key('buttons_parent_button_id_fkey', 'buttons', 'buttons', ['parent_button_id'], ['button_id'])
    # ### end Alembic commands ###
