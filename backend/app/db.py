from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)


def get_session():
    """Dependência do FastAPI: abre uma sessão por requisição e fecha no fim."""
    with Session(engine) as session:
        yield session
