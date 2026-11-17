# fastapi-clean-api

API REST de eventos em **FastAPI + SQLModel**, organizada em camadas por domínio,
com autenticação JWT (refresh token com rotação), migrações Alembic e deploy via
Docker + nginx.

## Para que serve

Esta é a base que uso para construir sites: um backend pronto com autenticação,
banco versionado por migrações e deploy. A cada projeto novo eu clono, troco o
domínio de exemplo (`eventos`) pelo do site e sigo a mesma estrutura de camadas.

## Destaques

- **Arquitetura em camadas por domínio:** cada domínio (`eventos`, `usuarios`,
  `auth`) tem `controller → service → repository`, mais `entity`, `dto` e
  `exceptions` próprios.
- **Autenticação:** JWT de acesso (15 min), refresh token com rotação e detecção
  de reuso, logout com revogação, hash de senha com Argon2 e limite de
  tentativas de login (429).
- **Migrações com Alembic** e proteções: backup automático do SQLite antes de
  migrar e script de verificação (hook de pre-commit / passo de CI) contra
  múltiplas heads e entidades sem migração.
- **Eventos:** rotas públicas (só publicados) e rotas admin (rascunhos incluídos,
  que nunca vazam pelas rotas públicas). Campo `imagem_url` validado (só
  http/https).
- **Deploy:** Docker Compose com API + nginx (rate limit, cache de 5 s no
  `GET /eventos`, limite de corpo, `/docs` escondido).

## Stack

Python · FastAPI · SQLModel · Pydantic Settings · Alembic · Argon2 · PyJWT ·
SQLite · Docker · nginx

## Estrutura

- `backend/`: a API (`app/<domínio>/`, `alembic/`, `scripts/`)
- `deploy/`: configuração do nginx
- `docker-compose.yml`: API + nginx para produção
- `frontend/`: reservado para um front futuro

## Rodar o backend em desenvolvimento

    cd backend
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # e troque a SECRET_KEY
    alembic upgrade head        # cria/atualiza as tabelas
    python -m app.criar_admin   # cria o primeiro usuário
    fastapi dev app/main.py

Docs interativas: http://127.0.0.1:8000/docs (só em desenvolvimento)

## Testes

    cd backend
    pip install -r requirements-dev.txt
    python -m pytest --cov=app

Cada teste roda num SQLite em memória novo (fixtures em `tests/conftest.py`), sem
tocar no banco de desenvolvimento. Cobrem eventos (rotas públicas, CRUD e admin),
auth (login, JWT inválido/vencido, refresh com rotação e reuso, logout), o limitador
de tentativas e o hash de senha. O GitHub Actions roda a verificação de migrações
e os testes a cada push.

## Migrações do banco (Alembic)

O esquema do banco é controlado por migrações em `backend/alembic/versions/`
(nada cria tabelas sozinho). Rode os comandos de dentro de `backend/`.

Mudou uma entidade (adicionou ou alterou um campo)?

    alembic revision --autogenerate -m "descrição curta"   # gera o script
    # LEIA o script gerado: renomear coluna vira "apaga e cria", ajuste à mão
    alembic upgrade head                                    # aplica

- Commite o arquivo de migração junto com a mudança da entidade.
- Nunca edite uma migração já aplicada em produção: corrija com uma nova.
- Voltar uma versão: `alembic downgrade -1`. Ver o estado: `alembic current`.
- Entidade em um domínio novo: importe o módulo em `alembic/env.py`, senão o
  Alembic não a enxerga.
- `alembic check` confirma que as entidades e o banco estão em sincronia.
- No Docker, `python -m app.migrar` roda a cada subida da API, antes do uvicorn.
  Se a migração falhar, o contêiner não sobe.

### Não perder o histórico das migrações

- **Os arquivos de `alembic/versions/` são código:** vão para o git e para a
  imagem Docker. O banco guarda só o número da versão em que está
  (`alembic_version`).
- **Backup automático:** com dados no banco e uma migração pendente, o
  `app.migrar` copia o SQLite para `backups/` (ao lado do banco, no volume)
  antes de migrar, e guarda os 5 mais recentes.
- **Versão desconhecida:** se o banco está numa versão que não existe em
  `alembic/versions/` (arquivo perdido), a subida falha com a mensagem
  explicando. Restaure o arquivo do git.
- **Verificação antes do commit:** `backend/scripts/verificar_migracoes.sh`
  falha se houver mais de uma head ou se uma entidade mudou sem migração.
  Ative o hook uma vez por clone:

      git config core.hooksPath .githooks

  O mesmo script serve de passo de CI.
- **Gerar uma migração** exige o banco na última versão: rode
  `alembic upgrade head` antes do `alembic revision --autogenerate`.
- Nunca edite nem apague uma migração já aplicada em produção.

## Autenticação

- `POST /auth/login` devolve `access_token` (JWT, 15 min) e `refresh_token`.
- `POST /auth/refresh` troca um refresh token por um par novo (rotação: cada
  refresh token vale uma vez; reusar um já usado encerra a sessão inteira).
- `POST /auth/logout` revoga o refresh token (responde sempre 204).
- `GET /auth/eu` devolve o usuário logado.
- Criar, editar e apagar eventos exige `Authorization: Bearer <access_token>`;
  `GET /eventos` é público.
- Depois de 5 logins errados em 15 min (por email ou por IP) o login responde 429.

## Deploy (Docker)

Pré-requisitos: Docker com Compose e um servidor Linux.

1. Crie `backend/.env` a partir do `backend/.env.example`:

       python -c "import secrets; print(secrets.token_hex(32))"   # SECRET_KEY
       chmod 600 backend/.env

   Defina `CORS_ORIGINS` com o endereço do site (ex.: `https://meusite.com.br`).
2. Suba:

       docker compose up -d --build

   As migrações rodam sozinhas ao subir a API (o banco é criado na primeira vez).
3. Crie o admin (a senha é pedida sem aparecer na tela):

       docker compose exec backend python -m app.criar_admin

4. Confira: `curl http://localhost/saude`

O nginx (porta 80) limita requisições por IP, faz cache de 5 s do
`GET /eventos`, recusa corpos acima de 1 MB e esconde `/docs`. A API não é
exposta diretamente, só pelo nginx. O banco fica no volume `dados`.

### HTTPS (obrigatório em produção)

Sem HTTPS o token trafega em texto puro. Duas opções:

- **Cloudflare** na frente (plano gratuito): termina o TLS, absorve ataques
  volumétricos e esconde o IP do servidor. Descomente o bloco `real_ip` no fim
  de `deploy/nginx.conf` para o limite por IP enxergar o visitante.
- **certbot** no próprio servidor, com um bloco `listen 443 ssl` no nginx.

### Operação

- **Um worker só:** o limitador de tentativas guarda os contadores em memória.
  Para escalar com vários processos, ele precisa ir para o Redis.
- **Trocar a senha de alguém:** `docker compose exec backend python -m app.alterar_senha`
  (encerra as sessões desse usuário).
- **Limpar refresh tokens vencidos:** `docker compose exec backend python -m app.limpar_tokens`;
  ponha no cron, uma vez por dia.
- **Backup:** copie o banco do volume, por exemplo
  `docker compose cp backend:/data/app.db ./backup-$(date +%F).db`.
- **Logs de login** (falhas e bloqueios): `docker compose logs backend | grep app.auth`.
- **Atualizar dependências:** as versões estão fixadas no `requirements.txt`;
  rode `pip-audit` de tempos em tempos.
