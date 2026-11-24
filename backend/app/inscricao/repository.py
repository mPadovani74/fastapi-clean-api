from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .entity import Inscricao
from .exceptions import InscricaoDuplicadaException


class InscricaoRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_evento_e_usuario(
        self, evento_id: int, usuario_id: int
    ) -> Inscricao | None:
        consulta = select(Inscricao).where(
            Inscricao.evento_id == evento_id, Inscricao.usuario_id == usuario_id
        )
        return self.session.exec(consulta).first()

    def find_by_evento(self, evento_id: int) -> list[Inscricao]:
        consulta = (
            select(Inscricao)
            .where(Inscricao.evento_id == evento_id)
            .order_by(Inscricao.criado_em)
        )
        return list(self.session.exec(consulta).all())

    def find_by_usuario(self, usuario_id: int) -> list[Inscricao]:
        consulta = (
            select(Inscricao)
            .where(Inscricao.usuario_id == usuario_id)
            .order_by(Inscricao.criado_em.desc())
        )
        return list(self.session.exec(consulta).all())

    def count_by_evento(self, evento_id: int) -> int:
        consulta = select(func.count()).select_from(Inscricao).where(
            Inscricao.evento_id == evento_id
        )
        return self.session.exec(consulta).one()

    def save(self, inscricao: Inscricao) -> Inscricao:
        self.session.add(inscricao)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise InscricaoDuplicadaException()
        self.session.refresh(inscricao)
        return inscricao

    def delete(self, inscricao: Inscricao) -> None:
        self.session.delete(inscricao)
        self.session.commit()
