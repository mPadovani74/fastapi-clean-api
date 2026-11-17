from ..auth.seguranca import hash_senha
from .dto import Tipo, UsuarioRequest, UsuarioResponse
from .repository import UsuarioRepository
from .entity import Usuario
from .exceptions import UsuarioNaoEncontradoException, EmailJaCadastradoException


class UsuarioService:

    def __init__(self, repository: UsuarioRepository):
        self.repository = repository
        

    def criar(self, request: UsuarioRequest, tipo: Tipo | None = None) -> Usuario:
        email = request.email.strip().lower()
        exist = self.repository.exists_by_email(email)

        if(exist):
            raise EmailJaCadastradoException(email)
        
        campos = {
            "email": email,
            "senha_hash": hash_senha(request.senha),
        }
        
        if tipo is not None:
            campos["tipo"] = tipo
        
        return self.repository.save(Usuario.model_validate(request, update=campos))

    def buscar_id(self, user_id: int) -> Usuario:
        usuario = self.repository.find_by_id(user_id)
        if usuario is None:
            raise UsuarioNaoEncontradoException(user_id)
        return usuario