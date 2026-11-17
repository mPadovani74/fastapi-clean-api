from datetime import datetime, timezone

from pydantic import AwareDatetime
from sqlalchemy import Integer
from sqlmodel import Field

from .dto import Tipo, UsuarioBase


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(UsuarioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    senha_hash: str
    tipo: Tipo = Field(default=Tipo.NORMAL, sa_type=Integer)
    ativo: bool = True
    data_criacao: AwareDatetime = Field(default_factory=agora_utc)
    data_atualizacao: AwareDatetime | None = None
