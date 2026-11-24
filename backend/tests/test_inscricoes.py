from datetime import date

import pytest

from app.auth.dependencies import usuario_atual
from app.auth.seguranca import hash_senha
from app.main import app
from app.usuarios.entity import Usuario


@pytest.fixture
def logar(session):
    def _logar(usuario: Usuario):
        app.dependency_overrides[usuario_atual] = lambda: usuario

    return _logar


@pytest.fixture
def outro_usuario(session):
    usuario = Usuario(
        nome="Bia",
        sobrenome="Lima",
        data_nascimento=date(1995, 5, 5),
        email="bia@exemplo.com",
        senha_hash=hash_senha("senha-de-teste-123"),
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def test_inscrever_usa_usuario_do_token(client, logar, usuario, criar_evento):
    logar(usuario)
    evento = criar_evento()

    resposta = client.post(f"/eventos/{evento.id}/inscricoes")

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["evento_id"] == evento.id
    assert corpo["usuario_id"] == usuario.id


def test_inscrever_ignora_usuario_id_do_body(
    client, logar, usuario, outro_usuario, criar_evento
):
    logar(usuario)
    evento = criar_evento()

    resposta = client.post(
        f"/eventos/{evento.id}/inscricoes", json={"usuario_id": outro_usuario.id}
    )

    assert resposta.json()["usuario_id"] == usuario.id


def test_inscrever_exige_autenticacao(client, criar_evento):
    evento = criar_evento()

    assert client.post(f"/eventos/{evento.id}/inscricoes").status_code == 401


def test_inscricao_repetida_devolve_409(client, logar, usuario, criar_evento):
    logar(usuario)
    evento = criar_evento()
    client.post(f"/eventos/{evento.id}/inscricoes")

    resposta = client.post(f"/eventos/{evento.id}/inscricoes")

    assert resposta.status_code == 409


def test_evento_inexistente_devolve_404(client, logar, usuario):
    logar(usuario)

    assert client.post("/eventos/999/inscricoes").status_code == 404


def test_rascunho_nao_aceita_inscricao(client, logar, usuario, criar_evento):
    logar(usuario)
    evento = criar_evento(publicado=False)

    assert client.post(f"/eventos/{evento.id}/inscricoes").status_code == 404


def test_evento_lotado_devolve_409(
    client, logar, usuario, outro_usuario, criar_evento
):
    evento = criar_evento(vagas=1)
    logar(usuario)
    assert client.post(f"/eventos/{evento.id}/inscricoes").status_code == 201

    logar(outro_usuario)
    resposta = client.post(f"/eventos/{evento.id}/inscricoes")

    assert resposta.status_code == 409


def test_vagas_nulas_significam_ilimitado(
    client, logar, usuario, outro_usuario, criar_evento
):
    evento = criar_evento(vagas=None)
    for quem in (usuario, outro_usuario):
        logar(quem)
        assert client.post(f"/eventos/{evento.id}/inscricoes").status_code == 201


def test_cancelar_libera_a_vaga(client, logar, usuario, outro_usuario, criar_evento):
    evento = criar_evento(vagas=1)
    logar(usuario)
    client.post(f"/eventos/{evento.id}/inscricoes")

    assert client.delete(f"/eventos/{evento.id}/inscricoes").status_code == 204

    logar(outro_usuario)
    assert client.post(f"/eventos/{evento.id}/inscricoes").status_code == 201


def test_cancelar_sem_inscricao_devolve_404(client, logar, usuario, criar_evento):
    logar(usuario)
    evento = criar_evento()

    assert client.delete(f"/eventos/{evento.id}/inscricoes").status_code == 404


def test_minhas_inscricoes_so_traz_as_do_usuario(
    client, logar, usuario, outro_usuario, criar_evento
):
    primeiro, segundo = criar_evento(), criar_evento(titulo="Outro")
    logar(usuario)
    client.post(f"/eventos/{primeiro.id}/inscricoes")
    logar(outro_usuario)
    client.post(f"/eventos/{segundo.id}/inscricoes")

    logar(usuario)
    ids = [i["evento_id"] for i in client.get("/inscricoes/minhas").json()]

    assert ids == [primeiro.id]


def test_admin_lista_inscritos_do_evento(
    client, logar, usuario, outro_usuario, criar_evento
):
    evento = criar_evento()
    for quem in (usuario, outro_usuario):
        logar(quem)
        client.post(f"/eventos/{evento.id}/inscricoes")

    resposta = client.get(f"/admin/eventos/{evento.id}/inscricoes")

    assert {i["usuario_id"] for i in resposta.json()} == {usuario.id, outro_usuario.id}


def test_admin_evento_inexistente_devolve_404(client, logar, usuario):
    logar(usuario)

    assert client.get("/admin/eventos/999/inscricoes").status_code == 404


def test_apagar_evento_apaga_as_inscricoes(client, logar, usuario, criar_evento):
    logar(usuario)
    evento = criar_evento()
    client.post(f"/eventos/{evento.id}/inscricoes")

    assert client.delete(f"/eventos/{evento.id}").status_code == 204

    assert client.get("/inscricoes/minhas").json() == []
