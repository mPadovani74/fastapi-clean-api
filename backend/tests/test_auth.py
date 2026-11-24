import jwt
import pytest

from app.auth.limitador import LimitadorTentativas
from app.config import settings

from .conftest import SENHA


def login(client, email="ana@exemplo.com", senha=SENHA):
    return client.post("/auth/login", json={"email": email, "senha": senha})


def cabecalho(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_valido_devolve_os_dois_tokens(client, usuario):
    resposta = login(client)

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["token_type"] == "bearer"
    assert dados["access_token"] and dados["refresh_token"]


def test_resposta_de_auth_nao_e_cacheada(client, usuario):
    assert login(client).headers["Cache-Control"] == "no-store"


def test_senha_errada_devolve_401(client, usuario):
    assert login(client, senha="errada-errada").status_code == 401


def test_email_inexistente_devolve_401(client, usuario):
    assert login(client, email="ninguem@exemplo.com").status_code == 401


def test_usuario_desativado_nao_entra(client, session, usuario):
    usuario.ativo = False
    session.add(usuario)
    session.commit()

    assert login(client).status_code == 401


def test_cinco_falhas_bloqueiam_com_429(client, usuario):
    for _ in range(5):
        assert login(client, senha="errada-errada").status_code == 401

    assert login(client).status_code == 429


def test_eu_devolve_o_usuario_logado(client, usuario):
    token = login(client).json()["access_token"]

    resposta = client.get("/auth/eu", headers=cabecalho(token))

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "ana@exemplo.com"
    assert "senha_hash" not in resposta.json()


def test_eu_sem_token_devolve_401(client):
    assert client.get("/auth/eu").status_code == 401


def test_token_malformado_devolve_401(client):
    assert client.get("/auth/eu", headers=cabecalho("lixo")).status_code == 401


def test_token_assinado_com_outra_chave_devolve_401(client, usuario):
    falso = jwt.encode({"sub": usuario.email, "exp": 9999999999}, "outra-chave-tambem-com-mais-de-32-bytes!", algorithm="HS256")

    assert client.get("/auth/eu", headers=cabecalho(falso)).status_code == 401


def test_token_vencido_devolve_401(client, usuario):
    vencido = jwt.encode(
        {"sub": usuario.email, "exp": 1}, settings.secret_key, algorithm=settings.algorithm
    )

    assert client.get("/auth/eu", headers=cabecalho(vencido)).status_code == 401


def test_token_sem_sub_devolve_401(client):
    sem_sub = jwt.encode({"exp": 9999999999}, settings.secret_key, algorithm=settings.algorithm)

    assert client.get("/auth/eu", headers=cabecalho(sem_sub)).status_code == 401


def test_token_de_usuario_desativado_devolve_401(client, session, usuario):
    token = login(client).json()["access_token"]
    usuario.ativo = False
    session.add(usuario)
    session.commit()

    assert client.get("/auth/eu", headers=cabecalho(token)).status_code == 401


def test_refresh_troca_por_um_par_novo(client, usuario):
    antigo = login(client).json()["refresh_token"]

    resposta = client.post("/auth/refresh", json={"refresh_token": antigo})

    assert resposta.status_code == 200
    assert resposta.json()["refresh_token"] != antigo


def test_refresh_token_vale_uma_vez(client, usuario):
    antigo = login(client).json()["refresh_token"]
    client.post("/auth/refresh", json={"refresh_token": antigo})

    assert client.post("/auth/refresh", json={"refresh_token": antigo}).status_code == 401


def test_reuso_de_refresh_encerra_a_sessao_inteira(client, usuario):
    antigo = login(client).json()["refresh_token"]
    novo = client.post("/auth/refresh", json={"refresh_token": antigo}).json()["refresh_token"]

    client.post("/auth/refresh", json={"refresh_token": antigo})

    assert client.post("/auth/refresh", json={"refresh_token": novo}).status_code == 401


def test_refresh_token_desconhecido_devolve_401(client):
    assert client.post("/auth/refresh", json={"refresh_token": "nao-existe"}).status_code == 401


def test_logout_revoga_o_refresh_token(client, usuario):
    refresh = login(client).json()["refresh_token"]

    assert client.post("/auth/logout", json={"refresh_token": refresh}).status_code == 204
    assert client.post("/auth/refresh", json={"refresh_token": refresh}).status_code == 401


def test_logout_com_token_desconhecido_tambem_devolve_204(client):
    assert client.post("/auth/logout", json={"refresh_token": "nao-existe"}).status_code == 204


def test_limitador_bloqueia_ao_atingir_o_maximo():
    lim = LimitadorTentativas(max_falhas=3, janela_segundos=60)
    for _ in range(2):
        lim.registrar_falha("a")
    assert not lim.bloqueado("a")

    lim.registrar_falha("a")

    assert lim.bloqueado("a")


def test_limitador_conta_cada_chave_separadamente():
    lim = LimitadorTentativas(max_falhas=1, janela_segundos=60)
    lim.registrar_falha("a")

    assert lim.bloqueado("a")
    assert not lim.bloqueado("b")


def test_limitador_zerar_libera_a_chave():
    lim = LimitadorTentativas(max_falhas=1, janela_segundos=60)
    lim.registrar_falha("a")
    lim.zerar("a")

    assert not lim.bloqueado("a")


def test_limitador_esquece_falhas_fora_da_janela(monkeypatch):
    agora = [1000.0]
    monkeypatch.setattr("app.auth.limitador.time.monotonic", lambda: agora[0])
    lim = LimitadorTentativas(max_falhas=1, janela_segundos=60)
    lim.registrar_falha("a")
    assert lim.bloqueado("a")

    agora[0] += 61

    assert not lim.bloqueado("a")
