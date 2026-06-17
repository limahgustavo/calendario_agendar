import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.auth_token import AuthToken
from app.models.enums import AuthTokenType


def create_auth_token(
    db: Session, user_id: uuid.UUID, tipo: AuthTokenType, ttl_hours: int = 48
) -> str:
    token = secrets.token_urlsafe(32)
    db.add(
        AuthToken(
            user_id=user_id,
            token=token,
            tipo=tipo,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
        )
    )
    db.flush()
    return token


def consume_auth_token(db: Session, token: str, tipo: AuthTokenType) -> AuthToken | None:
    """Valida o token e o marca como usado. Retorna o AuthToken ou None se inválido."""
    at = (
        db.query(AuthToken)
        .filter(AuthToken.token == token, AuthToken.tipo == tipo)
        .first()
    )
    if not at or at.used_at is not None:
        return None
    expires = at.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        return None
    at.used_at = datetime.now(timezone.utc)
    return at
