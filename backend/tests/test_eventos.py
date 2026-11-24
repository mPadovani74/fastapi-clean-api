from datetime import datetime, timedelta, timezone

import pytest

INICIO = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()


def corpo(**campos):
    return {"titulo": "Palestra", "inicio": INICIO, **campos}


def test_listagem_publica_so_traz_publicados_futuros(client, criar_evento):
    criar_evento(titulo="Futuro")
    criar_evento(titulo="Rascunho", publicado=False)
    criar_evento(titulo="Passado", inicio=datetime.now(timezone.utc) - timedelta(days=2))

    titulos = [e["titulo"] for e in client.get("/eventos").json()]

    assert titulos == ["Futuro"]


def test_listagem_publica_ordenada_por_inicio(client, criar_evento):
    agora = datetime.now(timezone.utc)
    criar_evento(titulo="Depois", inicio=agora + timedelta(days=9))
    criar_evento(titulo="Antes", inicio=agora + timedelta(days=2))

    titulos = [e["titulo"] for e in client.get("/eventos").json()]

    assert titulos == ["Antes", "Depois"]


def test_buscar_evento_publicado(client, criar_evento):
    evento = criar_evento()

    resposta = client.get(f"/eventos/{evento.id}")

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Culto"


def test_rascunho_nao_vaza_na_rota_publica(client, criar_evento):
    evento = criar_evento(publicado=False)

    assert client.get(f"/eventos/{evento.id}").status_code == 404


def test_evento_inexistente_devolve_404(client):
    assert client.get("/eventos/999").status_code == 404


@pytest.mark.parametrize(
    "metodo, url",
    [
        ("post", "/eventos"),
        ("patch", "/eventos/1"),
        ("delete", "/eventos/1"),
        ("get", "/admin/eventos"),
        ("get", "/admin/eventos/1"),
    ],
)
def test_rotas_protegidas_exigem_token(client, metodo, url):
    extra = {"json": corpo()} if metodo in ("post", "patch") else {}
    resposta = getattr(client, metodo)(url, **extra)

    assert resposta.status_code == 401


def test_criar_evento_devolve_201(client_admin):
    resposta = client_admin.post("/eventos", json=corpo(local="Salão"))

    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["id"] > 0
    assert dados["titulo"] == "Palestra"
    assert dados["local"] == "Salão"
    assert dados["publicado"] is True


def test_criar_exige_data_com_fuso(client_admin):
    resposta = client_admin.post("/eventos", json=corpo(inicio="2030-01-01T10:00:00"))

    assert resposta.status_code == 422


@pytest.mark.parametrize(
    "url",
    ["javascript:alert(1)", "data:text/html,oi", "ftp://exemplo.com/a.png", "sem-esquema"],
)
def test_imagem_url_so_aceita_http_e_https(client_admin, url):
    resposta = client_admin.post("/eventos", json=corpo(imagem_url=url))

    assert resposta.status_code == 422


def test_imagem_url_https_e_aceita(client_admin):
    resposta = client_admin.post("/eventos", json=corpo(imagem_url="https://exemplo.com/a.png"))

    assert resposta.status_code == 201
    assert resposta.json()["imagem_url"] == "https://exemplo.com/a.png"


def test_imagem_url_longa_demais_e_recusada(client_admin):
    url = "https://exemplo.com/" + "a" * 2048

    assert client_admin.post("/eventos", json=corpo(imagem_url=url)).status_code == 422


def test_patch_altera_so_os_campos_enviados(client_admin, criar_evento):
    evento = criar_evento(titulo="Antigo", local="Sala 1")

    resposta = client_admin.patch(f"/eventos/{evento.id}", json={"titulo": "Novo"})

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Novo"
    assert resposta.json()["local"] == "Sala 1"


def test_patch_com_null_limpa_imagem_url(client_admin, criar_evento):
    evento = criar_evento(imagem_url="https://exemplo.com/a.png")

    resposta = client_admin.patch(f"/eventos/{evento.id}", json={"imagem_url": None})

    assert resposta.json()["imagem_url"] is None


def test_patch_evento_inexistente_devolve_404(client_admin):
    assert client_admin.patch("/eventos/999", json={"titulo": "X"}).status_code == 404


def test_delete_devolve_204_e_remove(client_admin, criar_evento):
    evento = criar_evento()

    assert client_admin.delete(f"/eventos/{evento.id}").status_code == 204
    assert client_admin.get(f"/eventos/{evento.id}").status_code == 404


def test_delete_evento_inexistente_devolve_404(client_admin):
    assert client_admin.delete("/eventos/999").status_code == 404


def test_admin_lista_rascunhos_e_passados(client_admin, criar_evento):
    criar_evento(titulo="Rascunho", publicado=False)
    criar_evento(titulo="Passado", inicio=datetime.now(timezone.utc) - timedelta(days=3))

    titulos = [e["titulo"] for e in client_admin.get("/admin/eventos").json()]

    assert sorted(titulos) == ["Passado", "Rascunho"]


def test_admin_busca_rascunho_por_id(client_admin, criar_evento):
    evento = criar_evento(publicado=False)

    assert client_admin.get(f"/admin/eventos/{evento.id}").status_code == 200


def test_vagas_e_opcional_e_assume_sem_limite(client_admin):
    resposta = client_admin.post("/eventos", json=corpo())

    assert resposta.status_code == 201
    assert resposta.json()["vagas"] is None


def test_criar_evento_com_vagas(client_admin):
    resposta = client_admin.post("/eventos", json=corpo(vagas=50))

    assert resposta.status_code == 201
    assert resposta.json()["vagas"] == 50


def test_vagas_zero_e_aceita(client_admin):
    assert client_admin.post("/eventos", json=corpo(vagas=0)).status_code == 201


def test_vagas_negativas_sao_recusadas(client_admin):
    assert client_admin.post("/eventos", json=corpo(vagas=-1)).status_code == 422


def test_patch_altera_vagas(client_admin, criar_evento):
    evento = criar_evento(vagas=10)

    resposta = client_admin.patch(f"/eventos/{evento.id}", json={"vagas": 30})

    assert resposta.json()["vagas"] == 30


def test_patch_recusa_vagas_negativas(client_admin, criar_evento):
    evento = criar_evento(vagas=10)

    assert client_admin.patch(f"/eventos/{evento.id}", json={"vagas": -5}).status_code == 422


def test_evento_novo_tem_criado_em_e_nao_tem_alterado_em(client_admin):
    dados = client_admin.post("/eventos", json=corpo()).json()

    assert dados["criado_em"] is not None
    assert dados["alterado_em"] is None


def test_patch_preenche_alterado_em_sem_mexer_no_criado_em(client_admin):
    criado = client_admin.post("/eventos", json=corpo()).json()

    editado = client_admin.patch(f"/eventos/{criado['id']}", json={"titulo": "Novo"}).json()

    assert editado["alterado_em"] is not None
    assert editado["criado_em"] == criado["criado_em"]


def test_cliente_nao_consegue_forcar_criado_em(client_admin):
    resposta = client_admin.post("/eventos", json=corpo(criado_em="2000-01-01T00:00:00+00:00"))

    assert resposta.status_code == 201
    assert not resposta.json()["criado_em"].startswith("2000")
