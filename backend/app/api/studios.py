from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.crypto import encrypt, decrypt
from app.core.slug import unique_slug
from app.api.deps import get_current_studio, get_studio_by_slug
from app.models.user import User
from app.models.studio import Studio
from app.models.notification_log import NotificationLog
from app.models.enums import (
    UserRole,
    AuthTokenType,
    NotificationType,
    NotificationChannel,
)
from app.schemas.studio import (
    StudioRegisterRequest,
    StudioUpdateRequest,
    StudioResponse,
    StudioPublicResponse,
)
from app.services.tokens import create_auth_token
from app.services.resend import resend_service
from app.core.devlinks import log_link

router = APIRouter(prefix="/studios", tags=["studios"])


def _to_response(studio: Studio) -> StudioResponse:
    return StudioResponse(
        id=studio.id,
        name=studio.name,
        slug=studio.slug,
        email=studio.email,
        whatsapp=studio.whatsapp,
        payment_mode=studio.payment_mode,
        plano=studio.plano,
        pix_key=decrypt(studio.pix_key_enc),
        bank_info=decrypt(studio.bank_info_enc),
    )


@router.post("/register")
async def register_studio(data: StudioRegisterRequest, db: Session = Depends(get_db)):
    """Onboarding de nail designer: cria a conta (pendente de senha) + o studio."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing and existing.password_hash:
        raise HTTPException(status_code=400, detail="Email já cadastrado. Faça login.")

    user = existing or User(email=data.email, role=UserRole.NAIL_DESIGNER)
    user.name = data.designer_name
    user.whatsapp = data.whatsapp
    user.role = UserRole.NAIL_DESIGNER
    if not existing:
        db.add(user)
    db.flush()

    if db.query(Studio).filter(Studio.owner_id == user.id).first():
        raise HTTPException(status_code=400, detail="Este usuário já possui um studio.")

    studio = Studio(
        owner_id=user.id,
        name=data.studio_name,
        slug=unique_slug(db, data.studio_name),
        email=data.email,
        whatsapp=data.whatsapp,
    )
    db.add(studio)

    token = create_auth_token(db, user.id, AuthTokenType.SET_PASSWORD)
    db.commit()

    link = f"{settings.FRONTEND_URL}/auth/criar-senha/{token}"
    ok = await resend_service.send_set_password(user.email, user.name, link)
    db.add(
        NotificationLog(
            user_id=user.id,
            type=NotificationType.EMAIL_SET_PASSWORD,
            channel=NotificationChannel.EMAIL,
            recipient=user.email,
            success=ok,
        )
    )
    db.commit()
    log_link("criar-senha-studio", user.email, link, ok)

    return {
        "message": "Studio criado! Enviamos um link para criar sua senha.",
        "slug": studio.slug,
    }


@router.get("/me", response_model=StudioResponse)
def my_studio(studio: Studio = Depends(get_current_studio)):
    return _to_response(studio)


@router.put("/me", response_model=StudioResponse)
def update_my_studio(
    data: StudioUpdateRequest,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    payload = data.model_dump(exclude_unset=True)
    if "pix_key" in payload:
        studio.pix_key_enc = encrypt(payload.pop("pix_key"))
    if "bank_info" in payload:
        studio.bank_info_enc = encrypt(payload.pop("bank_info"))
    for field, value in payload.items():
        setattr(studio, field, value)
    db.commit()
    db.refresh(studio)
    return _to_response(studio)


@router.get("/{slug}/public", response_model=StudioPublicResponse)
def public_studio(studio: Studio = Depends(get_studio_by_slug)):
    return StudioPublicResponse(
        id=studio.id,
        name=studio.name,
        slug=studio.slug,
        payment_mode=studio.payment_mode,
        whatsapp=studio.whatsapp,
    )
