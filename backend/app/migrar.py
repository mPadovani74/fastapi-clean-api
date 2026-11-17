"""Aplica as migrações pendentes. Roda a cada subida da API no Docker.

Uso (a partir de backend/): python -m app.migrar

- Banco já na última versão: não faz nada.
- Banco novo (sem versão): cria tudo.
- Banco com dados e migração pendente (SQLite): copia o banco para
  `backups/` ao lado dele ANTES de migrar, e guarda só os 5 mais recentes.
- Banco numa versão que o código não conhece (arquivo de migração perdido):
  falha com erro claro. O contêiner não sobe, em vez de adivinhar.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.util.exc import CommandError

from .db import engine

MANTER_BACKUPS = 5


def _backup(versao_atual: str, versao_nova: str) -> None:
    if engine.url.get_backend_name() != "sqlite" or not engine.url.database:
        return  # em Postgres, o backup é do próprio banco (pg_dump)
    origem = Path(engine.url.database)
    pasta = origem.parent / "backups"
    pasta.mkdir(exist_ok=True)
    agora = datetime.now().strftime("%Y%m%d-%H%M%S")
    destino = pasta / f"{origem.stem}-{agora}-{versao_atual}-para-{versao_nova}.db"

    # API de backup do SQLite: cópia consistente mesmo com o banco em uso.
    conexao_origem, conexao_destino = sqlite3.connect(origem), sqlite3.connect(destino)
    try:
        conexao_origem.backup(conexao_destino)
    finally:
        conexao_destino.close()
        conexao_origem.close()
    destino.chmod(0o600)
    print(f"Backup antes de migrar: {destino}")

    for velho in sorted(pasta.glob(f"{origem.stem}-*.db"))[:-MANTER_BACKUPS]:
        velho.unlink()


def main() -> None:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    head = script.get_current_head()  # erro se houver mais de uma head

    with engine.connect() as conexao:
        atual = MigrationContext.configure(conexao).get_current_revision()

    if atual == head:
        print(f"Banco já está na versão {head}.")
        return

    if atual is not None:
        try:
            script.get_revision(atual)
        except CommandError:
            raise SystemExit(
                f"O banco está na versão {atual}, que não existe em alembic/versions/. "
                "Algum arquivo de migração foi perdido; restaure-o do git."
            )
        _backup(atual, head)

    print(f"Migrando: {atual or 'banco novo'} -> {head}")
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
