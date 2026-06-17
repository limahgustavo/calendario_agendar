import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    whatsapp: str | None = None
    celular: str | None = None


class SetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=6, max_length=100)


class UpdateMeRequest(BaseModel):
    name: str | None = None
    whatsapp: str | None = None
    celular: str | None = None
    cpf_cnpj: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    whatsapp: str | None = None
    celular: str | None = None
    cpf_cnpj: str | None = None
    role: UserRole
    email_verified: bool

    model_config = {"from_attributes": True}
