from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # noqa: F401  (registra todos os modelos no metadata)


def _bootstrap():
    """Garante tabelas, planos e configurações da plataforma (idempotente)."""
    from app.core.database import SessionLocal
    from app.models.plan import Plan
    from app.models.platform_settings import PlatformSettings

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        planos = [
            ("basico", 29.0, 10, ["Até 10 agendamentos/mês"]),
            ("premium", 79.0, 50, ["Até 50 agendamentos/mês", "Suporte prioritário"]),
            ("pro", 199.0, None, ["Agendamentos ilimitados", "Relatórios avançados"]),
        ]
        for nome, valor, limite, features in planos:
            if not db.query(Plan).filter(Plan.nome == nome).first():
                db.add(Plan(nome=nome, valor_mensal=valor, limite_agendamentos=limite, features=features))
        if not db.query(PlatformSettings).first():
            db.add(PlatformSettings(
                default_fee_pct=settings.PLATFORM_FEE_PCT,
                payout_weekday=settings.PAYOUT_WEEKDAY,
            ))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _bootstrap()
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (adicionados por fase)
from app.api import (  # noqa: E402
    auth,
    studios,
    services,
    availability,
    appointments,
    payments,
    dashboard,
    payouts,
    admin,
    plans,
)

app.include_router(auth.router, prefix="/api")
app.include_router(studios.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(availability.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(payouts.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(plans.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
