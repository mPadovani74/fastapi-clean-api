FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# Usuário sem privilégios; /data guarda o banco SQLite (volume)
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir /data && chown app /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

USER app

ENV ENVIRONMENT=production \
    DATABASE_URL=sqlite:////data/app.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saude', timeout=2)"

# UM worker só, de propósito: o limitador de tentativas guarda os contadores em
# memória, e com vários workers cada um teria o seu. --forwarded-allow-ips="*"
# é seguro porque a porta 8000 só é alcançável pelo nginx (rede do compose).
# python -m app.migrar: aplica as migrações pendentes (com backup do banco antes)
# e só então sobe a API. Se a migração falhar, o contêiner não sobe.
# "exec" deixa o uvicorn como processo principal (recebe os sinais de parada).
CMD ["sh", "-c", "python -m app.migrar && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'"]
