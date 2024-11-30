"""add download path

Revision ID: 5a6c34b27a81
Revises: 7fbf127dc198
Create Date: 2024-11-29 18:06:27.556648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a6c34b27a81'
down_revision: Union[str, None] = '7fbf127dc198'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('liked_tracks', sa.Column('download_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('liked_tracks', 'download_path')
    # ### end Alembic commands ###