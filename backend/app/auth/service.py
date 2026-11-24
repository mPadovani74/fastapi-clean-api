import uuid
from datetime import datetime, timedelta, timezone

from ..config import settings
from ..usuarios.repository import UsuarioRepository
from .dto import LoginRequest, TokenResponse
from .exceptions import CredenciaisInvalidas
from .refresh_token.entity import RefreshToken
from .refresh_token.repository import RefreshTokenRepository
from .seguranca import hash_senha, verificar_senha
from .tokens import criar_token, gerar_refresh_token, hash_refresh_token


_HASH_FALSO = hash_senha("senha-que-nunca-sera-usada")


class AuthService:

    def __init__(
        self,
        repository: UsuarioRepository,
        refresh_repository: RefreshTokenRepository,
    ):
        self.repository = repository
        self.refresh_repository = refresh_repository

    def login(self, payload: LoginRequest) -> TokenResponse:
        usuario = self.repository.find_by_email(payload.email)

        if usuario is None:
            verificar_senha(payload.senha, _HASH_FALSO)
            raise CredenciaisInvalidas()

        if not verificar_senha(payload.senha, usuario.senha_hash):
            raise CredenciaisInvalidas()

        if not usuario.ativo:
            raise CredenciaisInvalidas()

        familia = uuid.uuid4().hex
        return TokenResponse(
            access_token=criar_token(usuario.email),
            refresh_token=self._emitir_refresh_token(usuario.id, familia),
        )

    def refresh(self, token_recebido: str) -> TokenResponse:
        registro = self.refresh_repository.find_by_hash(
            hash_refresh_token(token_recebido)
        )
        if registro is None:
            raise CredenciaisInvalidas()

        if registro.revogado:
            self._revogar_familia(registro.familia)
            raise CredenciaisInvalidas()

        if registro.expira_em < datetime.now(timezone.utc):
            raise CredenciaisInvalidas()

        usuario = self.repository.find_by_id(registro.usuario_id)
        if usuario is None or not usuario.ativo:
            raise CredenciaisInvalidas()

        self.refresh_repository.revogar(registro)
        novo_refresh = self._emitir_refresh_token(usuario.id, registro.familia)

        return TokenResponse(
            access_token=criar_token(usuario.email),
            refresh_token=novo_refresh,
        )

    def logout(self, token_recebido: str) -> None:
        registro = self.refresh_repository.find_by_hash(
            hash_refresh_token(token_recebido)
        )
        if registro is not None:
            self._revogar_familia(registro.familia)

    def _emitir_refresh_token(self, usuario_id: int, familia: str) -> str:
        """Grava o hash no banco e devolve o token em texto puro."""
        token = gerar_refresh_token()
        self.refresh_repository.save(
            RefreshToken(
                usuario_id=usuario_id,
                token_hash=hash_refresh_token(token),
                familia=familia,
                expira_em=datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        return token

    def _revogar_familia(self, familia: str) -> None:
        for token in self.refresh_repository.find_by_familia(familia):
            if not token.revogado:
                self.refresh_repository.revogar(token)
