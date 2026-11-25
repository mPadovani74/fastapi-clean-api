from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from ..auth.dependencies import usuario_atual, usuario_id_atual
from ..db import get_session
from ..eventos.controller import get_evento_service
from ..eventos.service import EventoService
from .dto import InscricaoResponse
from .repository import InscricaoRepository
from .service import InscricaoService


def get_inscricao_repository(
    session: Session = Depends(get_session),
) -> InscricaoRepository:
    return InscricaoRepository(session)


def get_inscricao_service(
    repository: InscricaoRepository = Depends(get_inscricao_repository),
    eventos: EventoService = Depends(get_evento_service),
) -> InscricaoService:
    return InscricaoService(repository, eventos)


router = APIRouter(tags=["inscricoes"])


@router.post(
    "/eventos/{evento_id}/inscricoes",
    response_model=InscricaoResponse,
    status_code=201,
)
def inscrever(
    evento_id: int,
    usuario_id: int = Depends(usuario_id_atual),
    service: InscricaoService = Depends(get_inscricao_service),
):
    return service.inscrever(evento_id, usuario_id)


@router.get("/eventos/{evento_id}/inscricoes/minha", response_model=InscricaoResponse)
def buscar_inscricao_evento(
    evento_id: int,
    usuario_id: int = Depends(usuario_id_atual),
    service: InscricaoService = Depends(get_inscricao_service),
):
    return service.buscar_minha(evento_id, usuario_id)


@router.delete("/eventos/{evento_id}/inscricoes", status_code=204)
def cancelar(
    evento_id: int,
    usuario_id: int = Depends(usuario_id_atual),
    service: InscricaoService = Depends(get_inscricao_service),
):
    service.cancelar(evento_id, usuario_id)
    return Response(status_code=204)


@router.get("/inscricoes/minhas", response_model=list[InscricaoResponse])
def minhas(
    usuario_id: int = Depends(usuario_id_atual),
    service: InscricaoService = Depends(get_inscricao_service),
):
    return service.listar_do_usuario(usuario_id)


@router.get(
    "/admin/eventos/{evento_id}/inscricoes",
    response_model=list[InscricaoResponse],
    dependencies=[Depends(usuario_atual)],
)
def listar_do_evento(
    evento_id: int, service: InscricaoService = Depends(get_inscricao_service)
):
    return service.listar_do_evento(evento_id)
