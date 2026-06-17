"""Seed inicial. Uso: python seed.py (ou docker-compose exec backend python seed.py)"""
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.core.config import settings
import app.models  # noqa: F401
from app.models.user import User
from app.models.plan import Plan
from app.models.platform_settings import PlatformSettings
from app.models.enums import UserRole

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Admin geral
admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
if not admin:
    admin = User(
        name=settings.ADMIN_NAME,
        email=settings.ADMIN_EMAIL,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
        role=UserRole.ADMIN,
        email_verified=True,
    )
    db.add(admin)
    print(f"Admin criado: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
else:
    print("Admin já existe.")

# Planos
PLANOS = [
    ("basico", 29.0, 10, ["Até 10 agendamentos/mês"]),
    ("premium", 79.0, 50, ["Até 50 agendamentos/mês", "Suporte prioritário"]),
    ("pro", 199.0, None, ["Agendamentos ilimitados", "Relatórios avançados"]),
]
for nome, valor, limite, features in PLANOS:
    if not db.query(Plan).filter(Plan.nome == nome).first():
        db.add(Plan(nome=nome, valor_mensal=valor, limite_agendamentos=limite, features=features))
        print(f"Plano criado: {nome}")

# Configurações da plataforma (singleton)
if not db.query(PlatformSettings).first():
    db.add(
        PlatformSettings(
            default_fee_pct=settings.PLATFORM_FEE_PCT,
            payout_weekday=settings.PAYOUT_WEEKDAY,
        )
    )
    print("Configurações da plataforma criadas.")

db.commit()
db.close()
print("Seed concluído.")
