from datetime import datetime, timezone

from pydantic import AwareDatetime
from sqlmodel import Field, SQLModel


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class RefreshToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    token_hash: str = Field(unique=True, index=True)
    familia: str = Field(index=True)
    expira_em: AwareDatetime
    revogado: bool = False
    criado_em: AwareDatetime = Field(default_factory=agora_utc)
