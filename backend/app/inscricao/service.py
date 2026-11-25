from ..eventos.service import EventoService
from .entity import Inscricao
from .exceptions import (
    EventoLotadoException,
    InscricaoDuplicadaException,
    InscricaoNaoEncontradaException,
)
from .repository import InscricaoRepository


class InscricaoService:
    def __init__(self, repository: InscricaoRepository, eventos: EventoService):
        self.repository = repository
        self.eventos = eventos

    def inscrever(self, evento_id: int, usuario_id: int) -> Inscricao:
        evento = self.eventos.buscar_publicado(evento_id)

        if self.repository.find_by_evento_e_usuario(evento_id, usuario_id):
            raise InscricaoDuplicadaException()

        if evento.vagas is not None:
            if self.repository.count_by_evento(evento_id) >= evento.vagas:
                raise EventoLotadoException(evento_id)

        return self.repository.save(
            Inscricao(evento_id=evento_id, usuario_id=usuario_id)
        )

    def buscar_minha(self, evento_id: int, usuario_id: int) -> Inscricao:
        self.eventos.buscar_publicado(evento_id)
        inscricao = self.repository.find_by_evento_e_usuario(evento_id, usuario_id)
        if inscricao is None:
            raise InscricaoNaoEncontradaException()
        return inscricao

    def cancelar(self, evento_id: int, usuario_id: int) -> None:
        inscricao = self.repository.find_by_evento_e_usuario(evento_id, usuario_id)
        if inscricao is None:
            raise InscricaoNaoEncontradaException()
        self.repository.delete(inscricao)

    def listar_do_usuario(self, usuario_id: int) -> list[Inscricao]:
        return self.repository.find_by_usuario(usuario_id)

    def listar_do_evento(self, evento_id: int) -> list[Inscricao]:
        self.eventos.buscar_por_id(evento_id)
        return self.repository.find_by_evento(evento_id)
