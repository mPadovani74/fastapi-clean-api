"""adiciona imagem_url em evento

Revision ID: 9aafcdd0031a
Revises: e2f471899b4f
Create Date: 2026-11-11 15:40:51.031039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '9aafcdd0031a'
down_revision: Union[str, Sequence[str], None] = 'e2f471899b4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.add_column(sa.Column('imagem_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.drop_column('imagem_url')
