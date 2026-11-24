"""cria tabela inscricao

Revision ID: 6fac3bb0b225
Revises: 4177ad79d3f1
Create Date: 2026-11-24 18:31:14.536011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '6fac3bb0b225'
down_revision: Union[str, Sequence[str], None] = '4177ad79d3f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('inscricao',
    sa.Column('evento_id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('criado_em', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=False),
    sa.Column('alterado_em', sqlmodel.sql.sqltypes.UTCDateTime(), nullable=True),
    sa.ForeignKeyConstraint(['evento_id'], ['evento.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('evento_id', 'usuario_id', name='uq_inscricao_evento_usuario')
    )
    with op.batch_alter_table('inscricao', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_inscricao_evento_id'), ['evento_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_inscricao_usuario_id'), ['usuario_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('inscricao', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inscricao_usuario_id'))
        batch_op.drop_index(batch_op.f('ix_inscricao_evento_id'))

    op.drop_table('inscricao')
