from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Nail Booking SaaS"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 dias

    # Criptografia de dados sensíveis (PIX / banco). Fernet key opcional —
    # se vazia, é derivada do SECRET_KEY.
    ENCRYPTION_KEY: str = ""

    # Database (PostgreSQL)
    # DATABASE_URL é injetada em produção (Render/Railway). Local: monta de POSTGRES_*.
    DATABASE_URL: str = ""
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "nail_user"
    POSTGRES_PASSWORD: str = "nail_pass"
    POSTGRES_DB: str = "nail_booking"

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS / Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Asaas
    ASAAS_API_KEY: str = ""
    ASAAS_ENVIRONMENT: str = "sandbox"  # sandbox | production
    ASAAS_WEBHOOK_TOKEN: str = ""

    @property
    def ASAAS_BASE_URL(self) -> str:
        if self.ASAAS_ENVIRONMENT == "production":
            return "https://api.asaas.com/v3"
        return "https://sandbox.asaas.com/api/v3"

    # Z-API (WhatsApp)
    ZAPI_API_URL: str = "https://api.z-api.io"
    ZAPI_INSTANCE_ID: str = ""
    ZAPI_TOKEN: str = ""
    ZAPI_CLIENT_TOKEN: str = ""

    # Resend (Email)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@seudominio.com"
    EMAIL_FROM_NAME: str = "Nail Studio"

    # Plataforma / Repasses
    PLATFORM_FEE_PCT: float = 20.0  # taxa default do admin (%)
    PAYOUT_WEEKDAY: int = 4  # 0=segunda ... 4=sexta (Python weekday)

    # Admin default (usado no seed)
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "changeme123"
    ADMIN_NAME: str = "Administrador"


settings = Settings()
