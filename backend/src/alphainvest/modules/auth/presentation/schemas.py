from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    nombres: str = Field(min_length=1, max_length=100)
    apellidos: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    password: str = Field(min_length=12, max_length=128)
    version_terminos: str = Field(min_length=1, max_length=30)
    version_privacidad: str = Field(min_length=1, max_length=30)


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombres: str
    apellidos: str
    correo: str
    estado: str
    correo_verificado: bool
    roles: list[str]
    permisos: list[str]
