from datetime import datetime

from sqlalchemy import delete
from sqlmodel import Session, select

from ..inscricao.entity import Inscricao
from .entity import Evento


class EventoRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, evento_id: int) -> Evento | None:
        return self.session.get(Evento, evento_id)

    def find_publicados_a_partir_de(self, data: datetime) -> list[Evento]:
        consulta = (
            select(Evento)
            .where(Evento.publicado == True, Evento.inicio >= data)
            .order_by(Evento.inicio)
        )
        return list(self.session.exec(consulta).all())

    def find_todos(self) -> list[Evento]:
        """Todos, inclusive rascunhos e já realizados. Os mais recentes primeiro."""
        consulta = select(Evento).order_by(Evento.inicio.desc())
        return list(self.session.exec(consulta).all())

    def save(self, evento: Evento) -> Evento:
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        return evento

    def delete(self, evento: Evento) -> None:
        self.session.exec(delete(Inscricao).where(Inscricao.evento_id == evento.id))
        self.session.delete(evento)
        self.session.commit()

