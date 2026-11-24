import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth.controller import router as auth_router
from .auth.exceptions import CredenciaisInvalidas, MuitasTentativas
from .config import settings
from .eventos.controller import admin_router as eventos_admin_router
from .eventos.controller import router as eventos_router
from .eventos.exceptions import EventoNaoEncontradoException
from .inscricao.controller import router as inscricao_router
from .inscricao.exceptions import (
    EventoLotadoException,
    InscricaoDuplicadaException,
    InscricaoNaoEncontradaException,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


app = FastAPI(
    title="fastapi-clean-api",
    docs_url=None if settings.producao else "/docs",
    redoc_url=None if settings.producao else "/redoc",
    openapi_url=None if settings.producao else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_lista,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def headers_de_seguranca(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.url.path.startswith("/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(auth_router)
app.include_router(eventos_router)
app.include_router(eventos_admin_router)
app.include_router(inscricao_router)


@app.exception_handler(MuitasTentativas)
def muitas_tentativas(request: Request, exc: MuitasTentativas):
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(CredenciaisInvalidas)
def credenciais_invalidas(request: Request, exc: CredenciaisInvalidas):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(EventoNaoEncontradoException)
def evento_nao_encontrado(request: Request, exc: EventoNaoEncontradoException):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InscricaoDuplicadaException)
def inscricao_duplicada(request: Request, exc: InscricaoDuplicadaException):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EventoLotadoException)
def evento_lotado(request: Request, exc: EventoLotadoException):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InscricaoNaoEncontradaException)
def inscricao_nao_encontrada(request: Request, exc: InscricaoNaoEncontradaException):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.get("/saude")
def saude():
    return {"status": "ok"}
