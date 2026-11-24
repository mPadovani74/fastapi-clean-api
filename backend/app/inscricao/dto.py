from pydantic import AwareDatetime
from sqlmodel import SQLModel


class InscricaoBase(SQLModel):
    evento_id: int
    usuario_id: int


class InscricaoResponse(InscricaoBase):
    id: int
    criado_em: AwareDatetime
    alterado_em: AwareDatetime | None = None
