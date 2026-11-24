#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if [ -x .venv/bin/alembic ]; then ALEMBIC=.venv/bin/alembic; else ALEMBIC=alembic; fi
export SECRET_KEY="${SECRET_KEY:-chave-so-para-verificacao-das-migracoes}"

heads=$($ALEMBIC heads 2>/dev/null | grep -c "(head)" || true)
if [ "$heads" != "1" ]; then
    echo "ERRO: o histórico de migrações tem $heads heads (deveria ter 1)."
    echo "      Rode 'alembic merge heads -m \"junta ramos\"'."
    exit 1
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export DATABASE_URL="sqlite:///$tmp/verificacao.db"

$ALEMBIC upgrade head >/dev/null 2>&1 || { echo "ERRO: 'alembic upgrade head' falhou num banco novo."; exit 1; }

if ! saida=$($ALEMBIC check 2>&1); then
    echo "ERRO: as entidades têm mudanças sem migração."
    echo "      Rode: alembic revision --autogenerate -m \"descrição\""
    echo "$saida" | grep -E "Detected|New upgrade" || true
    exit 1
fi
echo "Migrações ok: 1 head, entidades e migrações em sincronia."
