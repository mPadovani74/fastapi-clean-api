"""Troca a senha de um usuário. Uso (a partir de backend/): python -m app.alterar_senha

Também revoga todos os refresh tokens do usuário: quem estava logado com a
senha antiga precisa entrar de novo.
"""
from getpass import getpass

from sqlmodel import Session, select

from .auth.refresh_token.entity import RefreshToken
from .auth.seguranca import hash_senha
from .db import engine
from .usuarios.repository import UsuarioRepository


def main() -> None:
    email = input("Email do usuário: ").strip().lower()
    senha = getpass("Nova senha (mínimo 8 caracteres): ")
    if senha != getpass("Confirme a nova senha: "):
        raise SystemExit("As senhas não conferem.")
    if not 8 <= len(senha) <= 128:
        raise SystemExit("A senha deve ter entre 8 e 128 caracteres.")

    with Session(engine) as session:
        repository = UsuarioRepository(session)
        usuario = repository.find_by_email(email)
        if usuario is None:
            raise SystemExit("Usuário não encontrado.")
        usuario.senha_hash = hash_senha(senha)
        repository.save(usuario)

        ativos = session.exec(
            select(RefreshToken).where(
                RefreshToken.usuario_id == usuario.id,
                RefreshToken.revogado == False,  # noqa: E712
            )
        ).all()
        for token in ativos:
            token.revogado = True
        session.commit()
    print(f"Senha alterada. {len(ativos)} sessão(ões) encerrada(s).")


if __name__ == "__main__":
    main()
