from datetime import date
from enum import IntEnum

from pydantic import AwareDatetime, EmailStr
from sqlmodel import Field, SQLModel


class Tipo(IntEnum):
    ADMIN = 1
    ASSOCIADO = 2
    NORMAL = 3
    COLABORADOR = 4


class UsuarioBase(SQLModel):
    nome: str
    sobrenome: str
    data_nascimento: date
    email: EmailStr


class UsuarioRequest(UsuarioBase):
    senha: str = Field(min_length=8)


class UsuarioResponse(UsuarioBase):
    id: int
    tipo: Tipo
    ativo: bool
    data_criacao: AwareDatetime
