class UsuarioNaoEncontradoException(Exception):
    def __init__(self, usuario_id: int):
        super().__init__(f"Usuário {usuario_id} não encontrado")
        self.usuario_id = usuario_id


class EmailJaCadastradoException(Exception):
    def __init__(self, email: str):
        super().__init__(f"O email {email} já está cadastrado")
        self.email = email
