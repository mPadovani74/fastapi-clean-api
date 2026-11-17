from datetime import datetime, timezone

from .dto import EventoRequest, EventoUpdateRequest
from .entity import Evento
from .exceptions import EventoNaoEncontradoException
from .repository import EventoRepository


class EventoService:
    def __init__(self, repository: EventoRepository):
        self.repository = repository

    def listar_proximos(self) -> list[Evento]:
        return self.repository.find_publicados_a_partir_de(datetime.now(timezone.utc))

    def listar_todos(self) -> list[Evento]:
        return self.repository.find_todos()

    def buscar_publicado(self, evento_id: int) -> Evento:
        evento = self.buscar_por_id(evento_id)
        if not evento.publicado:
            raise EventoNaoEncontradoException(evento_id)
        return evento

    def buscar_por_id(self, evento_id: int) -> Evento:
        evento = self.repository.find_by_id(evento_id)
        if evento is None:
            raise EventoNaoEncontradoException(evento_id)
        return evento

    def criar(self, request: EventoRequest) -> Evento:
        return self.repository.save(Evento.model_validate(request))

    def atualizar(self, evento_id: int, request: EventoUpdateRequest) -> Evento:
        evento = self.buscar_por_id(evento_id)
        evento.sqlmodel_update(request.model_dump(exclude_unset=True))
        return self.repository.save(evento)

    def apagar(self, evento_id: int) -> None:
        self.repository.delete(self.buscar_por_id(evento_id))
