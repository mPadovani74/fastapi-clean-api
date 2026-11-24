from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from ..eventos.entity import agora_utc
from .dto import InscricaoBase


class Inscricao(InscricaoBase, table=True):
    __table_args__ = (
        UniqueConstraint("evento_id", "usuario_id", name="uq_inscricao_evento_usuario"),
    )

    id: int | None = Field(default=None, primary_key=True)
    evento_id: int = Field(foreign_key="evento.id", index=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    criado_em: AwareDatetime = Field(default_factory=agora_utc)
    alterado_em: AwareDatetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": agora_utc}
    )
