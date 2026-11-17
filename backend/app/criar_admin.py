"""Cria um usuário admin. Uso: python -m app.criar_admin (a partir de backend/)."""
from datetime import date
from getpass import getpass

from pydantic import ValidationError
from sqlmodel import Session

from .db import engine
from .usuarios.dto import Tipo, UsuarioRequest
from .usuarios.exceptions import EmailJaCadastradoException
from .usuarios.repository import UsuarioRepository
from .usuarios.service import UsuarioService


def main() -> None:

    nome = input("Nome: ").strip()
    sobrenome = input("Sobrenome: ").strip()
    nascimento = date.fromisoformat(input("Data de nascimento (AAAA-MM-DD): ").strip())
    email = input("Email: ").strip()
    senha = getpass("Senha: ")
    if senha != getpass("Confirme a senha: "):
        raise SystemExit("As senhas não conferem.")

    try:
        request = UsuarioRequest(
            nome=nome,
            sobrenome=sobrenome,
            data_nascimento=nascimento,
            email=email,
            senha=senha,
        )
    except ValidationError as e:
        raise SystemExit(f"Dados inválidos:\n{e}")

    with Session(engine) as session:
        service = UsuarioService(UsuarioRepository(session))
        try:
            usuario = service.criar(request, tipo=Tipo.ADMIN)
        except EmailJaCadastradoException as e:
            raise SystemExit(str(e))
        print(f"Admin criado: id={usuario.id}, email={usuario.email}")


if __name__ == "__main__":
    main()
