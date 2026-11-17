from sqlmodel import Session, select
from .entity import Usuario


class UsuarioRepository:

    def __init__(self, session: Session):
        self.session = session
    
    def find_by_id(self, usuario_id : int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)
    
    def exists_by_email(self, usuario_email: str) -> bool:
        exists = (
            self.session.exec(select(Usuario).where(Usuario.email == usuario_email)
        ))
        return bool(exists.first())
    
    def find_by_email(self, usuario_email: str) -> Usuario | None:
        consulta = (
            select(Usuario)
            .where(Usuario.email == usuario_email)
        )
        exec = self.session.exec(consulta).first()

        return exec
    
    def save(self, usuario:Usuario) -> Usuario:
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario


