import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from ..config import settings


def criar_token(email: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": email, "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decodificar_token(token: str) -> dict:
    # "require": sem exp ou sem sub o token é recusado (o PyJWT, sozinho, só
    # valida o vencimento se o campo existir).
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        options={"require": ["exp", "sub"]},
    )


def gerar_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
