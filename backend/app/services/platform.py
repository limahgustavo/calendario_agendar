from sqlalchemy.orm import Session

from app.models.platform_settings import PlatformSettings
from app.models.studio import Studio


def get_settings(db: Session) -> PlatformSettings:
    s = db.query(PlatformSettings).first()
    if not s:
        s = PlatformSettings()
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def fee_pct_for(db: Session, studio: Studio) -> float:
    if studio.platform_fee_pct is not None:
        return float(studio.platform_fee_pct)
    return float(get_settings(db).default_fee_pct)
