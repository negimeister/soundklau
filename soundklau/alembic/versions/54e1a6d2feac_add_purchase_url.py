"""add purchase_url

Revision ID: 54e1a6d2feac
Revises: 87fb4177b6b5
Create Date: 2024-11-26 23:22:15.851613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54e1a6d2feac'
down_revision: Union[str, None] = '87fb4177b6b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('liked_tracks', sa.Column('purchase_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('liked_tracks', 'purchase_url')
    # ### end Alembic commands ###
