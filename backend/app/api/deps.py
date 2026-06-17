from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.studio import Studio
from app.models.enums import UserRole


def get_current_designer(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.NAIL_DESIGNER:
        raise HTTPException(status_code=403, detail="Acesso restrito a nail designers")
    return user


def get_current_studio(
    user: User = Depends(get_current_designer),
    db: Session = Depends(get_db),
) -> Studio:
    studio = db.query(Studio).filter(Studio.owner_id == user.id).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio não encontrado")
    return studio


def get_studio_by_slug(slug: str, db: Session = Depends(get_db)) -> Studio:
    studio = db.query(Studio).filter(Studio.slug == slug, Studio.is_active == True).first()  # noqa: E712
    if not studio:
        raise HTTPException(status_code=404, detail="Studio não encontrado")
    return studio


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return user
