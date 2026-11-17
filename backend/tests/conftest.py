import os

os.environ.setdefault("SECRET_KEY", "chave-so-para-os-testes-com-mais-de-32-bytes")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.auth.dependencies import usuario_atual
from app.auth.limitador import limitador
from app.auth.seguranca import hash_senha
from app.db import get_session
from app.eventos.entity import Evento
from app.main import app
from app.usuarios.entity import Usuario

SENHA = "senha-de-teste-123"


@pytest.fixture
def session():
    """Um SQLite em memória novo por teste: isolamento total."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # todas as conexões enxergam o mesmo banco em memória
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def zerar_limitador():
    limitador._falhas.clear()


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_admin(client):
    """Cliente já autenticado: troca a dependência de auth por um usuário qualquer."""
    app.dependency_overrides[usuario_atual] = lambda: object()
    return client


def _criar_evento(session: Session, **campos) -> Evento:
    agora = datetime.now(timezone.utc)
    dados = {"titulo": "Culto", "inicio": agora + timedelta(days=7), **campos}
    evento = Evento(**dados)
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


@pytest.fixture
def criar_evento(session):
    return lambda **campos: _criar_evento(session, **campos)


@pytest.fixture
def usuario(session):
    usuario = Usuario(
        nome="Ana",
        sobrenome="Souza",
        data_nascimento=date(1990, 1, 1),
        email="ana@exemplo.com",
        senha_hash=hash_senha(SENHA),
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario
