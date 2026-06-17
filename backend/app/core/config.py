from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Nail Designer Booking"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8h

    # Database
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Asaas
    ASAAS_API_KEY: str
    ASAAS_ENVIRONMENT: str = "sandbox"  # sandbox | production
    ASAAS_WEBHOOK_TOKEN: str

    @property
    def ASAAS_BASE_URL(self) -> str:
        if self.ASAAS_ENVIRONMENT == "production":
            return "https://api.asaas.com/v3"
        return "https://sandbox.asaas.com/api/v3"

    # Z-API (WhatsApp)
    # ZAPI_API_URL: URL base da instância (ex: https://api.z-api.io ou URL customizada do plano)
    ZAPI_API_URL: str = "https://api.z-api.io"
    ZAPI_INSTANCE_ID: str = ""
    ZAPI_TOKEN: str = ""
    ZAPI_CLIENT_TOKEN: str = ""

    # Resend (Email)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@seudominio.com"
    EMAIL_FROM_NAME: str = "Nail Designer"

    # Admin default (usado na migration seed)
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "changeme123"


settings = Settings()
