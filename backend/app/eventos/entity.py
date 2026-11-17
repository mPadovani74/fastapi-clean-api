from sqlmodel import Field

from .dto import EventoBase


class Evento(EventoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
