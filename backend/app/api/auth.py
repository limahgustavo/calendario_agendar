from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models.user import User
from app.models.notification_log import NotificationLog
from app.models.enums import (
    UserRole,
    AuthTokenType,
    NotificationType,
    NotificationChannel,
)
from app.schemas.auth import (
    RegisterRequest,
    SetPasswordRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateMeRequest,
    TokenResponse,
    UserResponse,
)
from app.services.tokens import create_auth_token, consume_auth_token
from app.services.resend import resend_service
from app.core.devlinks import log_link

router = APIRouter(prefix="/auth", tags=["auth"])


def _log_email(db, user_id, ntype, recipient, ok):
    db.add(
        NotificationLog(
            user_id=user_id,
            type=ntype,
            channel=NotificationChannel.EMAIL,
            recipient=recipient,
            success=ok,
        )
    )


@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Auto-cadastro de cliente. Cria conta pendente e envia link para criar senha."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing and existing.password_hash:
        raise HTTPException(status_code=400, detail="Email já cadastrado. Faça login.")

    user = existing or User(email=data.email, role=UserRole.CLIENTE)
    user.name = data.name
    user.whatsapp = data.whatsapp
    user.celular = data.celular
    if not existing:
        db.add(user)
    db.flush()

    token = create_auth_token(db, user.id, AuthTokenType.SET_PASSWORD)
    db.commit()

    link = f"{settings.FRONTEND_URL}/auth/criar-senha/{token}"
    ok = await resend_service.send_set_password(user.email, user.name, link)
    _log_email(db, user.id, NotificationType.EMAIL_SET_PASSWORD, user.email, ok)
    db.commit()
    log_link("criar-senha", user.email, link, ok)

    return {"message": "Enviamos um link para criar sua senha no seu email."}


@router.post("/set-password", response_model=TokenResponse)
def set_password(data: SetPasswordRequest, db: Session = Depends(get_db)):
    at = consume_auth_token(db, data.token, AuthTokenType.SET_PASSWORD)
    if not at:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    user = db.get(User, at.user_id)
    user.password_hash = hash_password(data.password)
    user.email_verified = True
    db.commit()
    access = create_access_token(str(user.id))
    return TokenResponse(access_token=access, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")
    access = create_access_token(str(user.id))
    return TokenResponse(access_token=access, role=user.role)


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user and user.password_hash:
        token = create_auth_token(db, user.id, AuthTokenType.RESET_PASSWORD, ttl_hours=2)
        db.commit()
        link = f"{settings.FRONTEND_URL}/auth/redefinir/{token}"
        ok = await resend_service.send_reset_password(user.email, user.name, link)
        _log_email(db, user.id, NotificationType.EMAIL_RESET_PASSWORD, user.email, ok)
        db.commit()
        log_link("redefinir-senha", user.email, link, ok)
    # resposta genérica (não revela se o email existe)
    return {"message": "Se o email existir, enviaremos um link de redefinição."}


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    at = consume_auth_token(db, data.token, AuthTokenType.RESET_PASSWORD)
    if not at:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    user = db.get(User, at.user_id)
    user.password_hash = hash_password(data.password)
    db.commit()
    access = create_access_token(str(user.id))
    return TokenResponse(access_token=access, role=user.role)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UpdateMeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
