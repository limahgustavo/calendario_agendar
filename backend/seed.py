"""Run once to create the admin user. Usage: python seed.py"""
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.core.config import settings
from app.models.user import User
import app.models  # noqa

Base.metadata.create_all(bind=engine)

db = SessionLocal()
existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
if not existing:
    admin = User(
        name="Nail Designer",
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(admin)
    db.commit()
    print(f"Admin criado: {settings.ADMIN_EMAIL}")
else:
    print("Admin já existe.")
db.close()
