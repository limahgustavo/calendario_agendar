from app.core.database import SessionLocal
from app.services.payouts import generate_payouts_for_week
from app.tasks.celery_app import celery_app


@celery_app.task
def generate_weekly_payouts():
    db = SessionLocal()
    try:
        created = generate_payouts_for_week(db)
        return len(created)
    finally:
        db.close()
