from datetime import datetime, timezone

from pydantic import AwareDatetime
from sqlmodel import Field

from .dto import EventoBase


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class Evento(EventoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    criado_em: AwareDatetime = Field(default_factory=agora_utc)
    alterado_em: AwareDatetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": agora_utc}
    )
