import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_studio
from app.models.plan import Plan
from app.models.studio import Studio
from app.models.subscription import Subscription
from app.models.enums import StudioPlan, SubscriptionStatus
from app.schemas.plan import PlanResponse, SubscribeRequest
from app.services.asaas import asaas_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).filter(Plan.is_active == True).order_by(Plan.valor_mensal).all()  # noqa: E712


@router.post("/studio/subscribe", response_model=PlanResponse)
async def subscribe(
    data: SubscribeRequest,
    studio: Studio = Depends(get_current_studio),
    db: Session = Depends(get_db),
):
    plan = db.get(Plan, data.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    try:
        studio.plano = StudioPlan(plan.nome)
    except ValueError:
        raise HTTPException(status_code=400, detail="Plano inválido")

    # Assinatura recorrente no Asaas (best-effort — não bloqueia a troca de plano)
    asaas_sub_id = None
    if float(plan.valor_mensal) > 0:
        try:
            owner = studio.owner
            customer_id = await asaas_service.find_or_create_customer(
                owner.name, owner.email, owner.whatsapp or "", owner.cpf_cnpj
            )
            res = await asaas_service.create_subscription(
                customer_id,
                float(plan.valor_mensal),
                f"Plano {plan.nome} - {studio.name}",
                (date.today() + timedelta(days=7)).isoformat(),
            )
            asaas_sub_id = res.get("asaas_subscription_id")
        except Exception as e:
            logger.error("Falha ao criar assinatura Asaas: %s", e, exc_info=True)

    today = date.today()
    sub = db.query(Subscription).filter(Subscription.studio_id == studio.id).first()
    if sub:
        sub.plan_id = plan.id
        sub.status = SubscriptionStatus.ACTIVE
        sub.asaas_subscription_id = asaas_sub_id or sub.asaas_subscription_id
        sub.current_period_start = today
        sub.current_period_end = today + timedelta(days=30)
    else:
        sub = Subscription(
            studio_id=studio.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            asaas_subscription_id=asaas_sub_id,
            current_period_start=today,
            current_period_end=today + timedelta(days=30),
        )
        db.add(sub)
    db.commit()
    return plan
