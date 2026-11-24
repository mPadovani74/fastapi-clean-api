"""adiciona vagas e datas de auditoria em evento

Revision ID: 4177ad79d3f1
Revises: 9aafcdd0031a
Create Date: 2026-11-23 17:09:36.363638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '4177ad79d3f1'
down_revision: Union[str, Sequence[str], None] = '9aafcdd0031a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vagas', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('criado_em', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False, server_default=sa.func.now()))
        batch_op.add_column(sa.Column('alterado_em', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('evento', schema=None) as batch_op:
        batch_op.drop_column('alterado_em')
        batch_op.drop_column('criado_em')
        batch_op.drop_column('vagas')
