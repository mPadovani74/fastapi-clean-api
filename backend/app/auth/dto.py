from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(SQLModel):
    refresh_token: str = Field(max_length=200)


class LoginRequest(SQLModel):
    email: EmailStr
    senha: str = Field(max_length=128)