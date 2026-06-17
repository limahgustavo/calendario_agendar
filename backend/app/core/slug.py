import re
import unicodedata

from sqlalchemy.orm import Session


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "studio"


def unique_slug(db: Session, base: str) -> str:
    from app.models.studio import Studio

    base = slugify(base)
    slug = base
    i = 2
    while db.query(Studio).filter(Studio.slug == slug).first():
        slug = f"{base}-{i}"
        i += 1
    return slug
