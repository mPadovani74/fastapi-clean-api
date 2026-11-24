from urllib.parse import urlparse

from pydantic import AwareDatetime, field_validator
from sqlmodel import Field, SQLModel


class EventoBase(SQLModel):
    titulo: str
    descricao: str = ""
    inicio: AwareDatetime
    fim: AwareDatetime | None = None
    local: str = ""
    link_inscricao: str | None = None
    imagem_url: str | None = None
    publicado: bool = True
    vagas: int | None = Field(default=None, ge=0)


def _somente_http(valor: str | None) -> str | None:
    """Aceita só links http(s). Bloqueia javascript:, data: etc., que virariam
    XSS se o front colocasse o valor num href ou num src."""
    if valor is None or valor == "":
        return valor
    if len(valor) > 2048:
        raise ValueError("a URL é longa demais (máximo 2048 caracteres)")
    partes = urlparse(valor)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        raise ValueError("deve ser uma URL http ou https")
    return valor


class EventoRequest(EventoBase):
    _validar_link = field_validator("link_inscricao", "imagem_url")(_somente_http)


class EventoUpdateRequest(SQLModel):
    _validar_link = field_validator("link_inscricao", "imagem_url")(_somente_http)

    titulo: str | None = None
    descricao: str | None = None
    inicio: AwareDatetime | None = None
    fim: AwareDatetime | None = None
    local: str | None = None
    link_inscricao: str | None = None
    imagem_url: str | None = None
    publicado: bool | None = None
    vagas: int | None = Field(default=None, ge=0)


class EventoResponse(EventoBase):
    id: int
    criado_em: AwareDatetime
    alterado_em: AwareDatetime | None = None
