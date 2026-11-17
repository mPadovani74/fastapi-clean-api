import logging

from fastapi import APIRouter, Depends, Request, Response
from ..usuarios.dto import UsuarioResponse
from ..usuarios.entity import Usuario
from ..usuarios.repository import UsuarioRepository
from .dependencies import (
    get_refresh_repository,
    get_usuario_repository,
    usuario_atual,
)
from .dto import LoginRequest, RefreshRequest, TokenResponse
from .exceptions import CredenciaisInvalidas, MuitasTentativas
from .limitador import limitador
from .refresh_token.repository import RefreshTokenRepository
from .service import AuthService


def get_login_service(
        repository: UsuarioRepository = Depends(get_usuario_repository),
        refresh_repository: RefreshTokenRepository = Depends(get_refresh_repository),
) -> AuthService:
    return AuthService(repository, refresh_repository)

log = logging.getLogger("app.auth")

router = APIRouter(prefix="/auth", tags=["auth"])
    

@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    http_request: Request,
    service: AuthService = Depends(get_login_service),
):
    chave_email = f"email:{request.email.strip().lower()}"
    chave_ip = f"ip:{http_request.client.host if http_request.client else 'desconhecido'}"

    if limitador.bloqueado(chave_email) or limitador.bloqueado(chave_ip):
        log.warning("login bloqueado por excesso de tentativas: %s %s", chave_ip, chave_email)
        raise MuitasTentativas()

    try:
        token = service.login(request)
    except CredenciaisInvalidas:
        log.warning("login falhou: %s %s", chave_ip, chave_email)
        limitador.registrar_falha(chave_email)
        limitador.registrar_falha(chave_ip)
        raise
    limitador.zerar(chave_email)
    return token


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: RefreshRequest,
    service: AuthService = Depends(get_login_service),
):
    return service.refresh(request.refresh_token)


@router.post("/logout", status_code=204)
def logout(
    request: RefreshRequest,
    service: AuthService = Depends(get_login_service),
):
    service.logout(request.refresh_token)
    return Response(status_code=204)


@router.get("/eu", response_model=UsuarioResponse)
def eu(usuario: Usuario = Depends(usuario_atual)):
    return usuario