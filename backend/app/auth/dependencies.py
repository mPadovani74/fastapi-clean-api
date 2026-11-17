from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlmodel import Session

from ..db import get_session
from ..usuarios.entity import Usuario
from ..usuarios.repository import UsuarioRepository
from .exceptions import CredenciaisInvalidas
from .refresh_token.repository import RefreshTokenRepository
from .tokens import decodificar_token

# auto_error=False: sem header ele devolve None e o 401 é decidido aqui.
bearer = HTTPBearer(auto_error=False)


def get_usuario_repository(
    session: Session = Depends(get_session),
) -> UsuarioRepository:
    return UsuarioRepository(session)


def get_refresh_repository(
    session: Session = Depends(get_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def usuario_atual(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    repository: UsuarioRepository = Depends(get_usuario_repository),
) -> Usuario:
    if credentials is None:
        raise CredenciaisInvalidas()

    try:
        payload = decodificar_token(credentials.credentials)
    except PyJWTError:
        raise CredenciaisInvalidas()

    email = payload.get("sub")
    if email is None:
        raise CredenciaisInvalidas()

    # Usuário apagado ou desativado depois que o token foi emitido.
    usuario = repository.find_by_email(email)
    if usuario is None or not usuario.ativo:
        raise CredenciaisInvalidas()

    return usuario
