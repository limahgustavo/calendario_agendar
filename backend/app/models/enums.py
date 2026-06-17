import enum


class UserRole(str, enum.Enum):
    CLIENTE = "cliente"
    NAIL_DESIGNER = "nail_designer"
    ADMIN = "admin"


class PaymentMode(str, enum.Enum):
    DEPOSIT_50 = "deposit_50"  # cobra 50% antecipado, 50% presencial
    FULL_100 = "full_100"  # cobra 100% antecipado


class ServiceCategory(str, enum.Enum):
    APLICACAO = "aplicacao"
    MANUTENCAO = "manutencao"
    OUTROS = "outros"


class StudioPlan(str, enum.Enum):
    BASICO = "basico"
    PREMIUM = "premium"
    PRO = "pro"


class AppointmentStatus(str, enum.Enum):
    AGENDADO = "agendado"  # criado, aguardando pagamento
    CONFIRMADO = "confirmado"  # pago
    CANCELADO = "cancelado"
    REALIZADO = "realizado"
    REMARCADO = "remarcado"


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"  # sinal (50%)
    FULL = "full"  # valor cheio (100%)
    REMAINDER = "remainder"  # saldo restante


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PayoutStatus(str, enum.Enum):
    PENDENTE_APROVACAO = "pendente_aprovacao"
    APROVADO = "aprovado"
    TRANSFERIDO = "transferido"
    BLOQUEADO = "bloqueado"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class NotificationType(str, enum.Enum):
    EMAIL_CONFIRMATION = "email_confirmation"
    WHATSAPP_CONFIRMATION = "whatsapp_confirmation"
    WHATSAPP_REMINDER_24H = "whatsapp_reminder_24h"
    WHATSAPP_REMINDER_2H = "whatsapp_reminder_2h"
    EMAIL_REMINDER = "email_reminder"
    EMAIL_SET_PASSWORD = "email_set_password"
    EMAIL_RESET_PASSWORD = "email_reset_password"
    EMAIL_WELCOME = "email_welcome"
    EMAIL_PAYOUT = "email_payout"


class NotificationChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"


class AuthTokenType(str, enum.Enum):
    SET_PASSWORD = "set_password"
    RESET_PASSWORD = "reset_password"
