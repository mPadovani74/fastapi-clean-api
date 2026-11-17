from app.auth.seguranca import hash_senha, verificar_senha


def test_hash_nao_guarda_a_senha_em_texto_puro():
    assert "segredo123" not in hash_senha("segredo123")


def test_mesma_senha_gera_hashes_diferentes_por_causa_do_salt():
    assert hash_senha("segredo123") != hash_senha("segredo123")


def test_verificar_senha_certa_e_errada():
    h = hash_senha("segredo123")

    assert verificar_senha("segredo123", h) is True
    assert verificar_senha("outra-coisa", h) is False
