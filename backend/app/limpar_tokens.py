"""Apaga refresh tokens vencidos há mais de 1 dia.

Uso (a partir de backend/): python -m app.limpar_tokens
Pensado para rodar uma vez por dia no cron.

Por que esperar 1 dia depois do vencimento: um token revogado precisa continuar
na tabela para o reuso dele ser detectado. Depois de vencido ele seria
recusado de qualquer forma, então aí já pode sumir.
"""
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from .auth.refresh_token.entity import RefreshToken
from .db import engine


def main() -> None:
    limite = datetime.now(timezone.utc) - timedelta(days=1)
    with Session(engine) as session:
        antigos = session.exec(
            select(RefreshToken).where(RefreshToken.expira_em < limite)
        ).all()
        for token in antigos:
            session.delete(token)
        session.commit()
    print(f"{len(antigos)} refresh token(s) removido(s).")


if __name__ == "__main__":
    main()
