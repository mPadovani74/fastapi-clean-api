from sqlmodel import select
from sqlmodel import Session
from ..refresh_token.entity import RefreshToken


class RefreshTokenRepository:

    def __init__(self,session:Session):
        self.session = session


    def save(self, refresh_token:RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        self.session.commit()
        self.session.refresh(refresh_token)
        return refresh_token
    
    def find_by_hash(self, token_hash:str):
        consulta =  (select(RefreshToken)
                    .where(RefreshToken.token_hash == token_hash)
                    )

        return (self.session.exec(consulta).first())
    
    def find_by_familia(self, familia:str) -> List[RefreshToken]:
          consulta =  (select(RefreshToken)
                    .where(RefreshToken.familia == familia))
          return list(self.session.exec(consulta))
    

    def revogar(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.revogado = True
        return self.save(refresh_token)