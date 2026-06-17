from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "nail_booking",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.reminders", "app.tasks.payouts"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
)

# Repasses semanais (sexta-feira às 20h, horário de São Paulo)
celery_app.conf.beat_schedule = {
    "weekly-payouts": {
        "task": "app.tasks.payouts.generate_weekly_payouts",
        "schedule": crontab(day_of_week="fri", hour=20, minute=0),
    },
}
