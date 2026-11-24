from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from ..auth.dependencies import usuario_atual
from ..db import get_session
from .dto import EventoRequest, EventoResponse, EventoUpdateRequest
from .repository import EventoRepository
from .service import EventoService


def get_evento_repository(session: Session = Depends(get_session)) -> EventoRepository:
    return EventoRepository(session)


def get_evento_service(
    repository: EventoRepository = Depends(get_evento_repository),
) -> EventoService:
    return EventoService(repository)


router = APIRouter(prefix="/eventos", tags=["eventos"])

admin_router = APIRouter(
    prefix="/admin/eventos",
    tags=["eventos (admin)"],
    dependencies=[Depends(usuario_atual)],
)


@admin_router.get("", response_model=list[EventoResponse])
def listar_todos(service: EventoService = Depends(get_evento_service)):
    return service.listar_todos()


@admin_router.get("/{evento_id}", response_model=EventoResponse)
def buscar_qualquer(evento_id: int, service: EventoService = Depends(get_evento_service)):
    return service.buscar_por_id(evento_id)


@router.get("", response_model=list[EventoResponse])
def listar_proximos(service: EventoService = Depends(get_evento_service)):
    return service.listar_proximos()


@router.get("/{evento_id}", response_model=EventoResponse)
def buscar(evento_id: int, service: EventoService = Depends(get_evento_service)):
    return service.buscar_publicado(evento_id)


@router.post("", response_model=EventoResponse,dependencies=[Depends(usuario_atual)], status_code=201)
def criar(request: EventoRequest, service: EventoService = Depends(get_evento_service)):
    return service.criar(request)


@router.patch("/{evento_id}", response_model=EventoResponse,dependencies=[Depends(usuario_atual)])
def atualizar(
    evento_id: int,
    request: EventoUpdateRequest,
    service: EventoService = Depends(get_evento_service),
):
    return service.atualizar(evento_id, request)


@router.delete("/{evento_id}", dependencies=[Depends(usuario_atual)], status_code=204)
def apagar(evento_id: int, service: EventoService = Depends(get_evento_service)):
    service.apagar(evento_id)
    return Response(status_code=204)
