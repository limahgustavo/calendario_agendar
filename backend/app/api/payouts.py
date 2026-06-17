import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.payout import Payout
from app.models.user import User
from app.models.enums import PayoutStatus
from app.schemas.payout import PayoutResponse
from app.services.payouts import generate_payouts_for_week, approve_payout

router = APIRouter(prefix="/payouts", tags=["payouts"])


def _to_response(p: Payout) -> PayoutResponse:
    return PayoutResponse(
        id=p.id,
        studio_id=p.studio_id,
        studio_name=p.studio.name if p.studio else None,
        semana_inicio=p.semana_inicio,
        valor_bruto=float(p.valor_bruto),
        taxa_admin_pct=float(p.taxa_admin_pct),
        taxa_admin_valor=float(p.taxa_admin_valor),
        valor_liquido=float(p.valor_liquido),
        status=p.status,
        asaas_transfer_id=p.asaas_transfer_id,
        transferido_at=p.transferido_at,
    )


@router.get("", response_model=list[PayoutResponse])
def list_payouts(
    status_filter: PayoutStatus | None = Query(None, alias="status"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Payout)
    if status_filter:
        q = q.filter(Payout.status == status_filter)
    return [_to_response(p) for p in q.order_by(Payout.semana_inicio.desc()).all()]


@router.post("/gerar")
def generate_now(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    created = generate_payouts_for_week(db)
    return {"criados": len(created)}


@router.post("/{payout_id}/aprovar", response_model=PayoutResponse)
async def approve(
    payout_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    payout = db.get(Payout, payout_id)
    if not payout:
        raise HTTPException(status_code=404, detail="Repasse não encontrado")
    if payout.status == PayoutStatus.TRANSFERIDO:
        raise HTTPException(status_code=400, detail="Repasse já transferido")
    try:
        await approve_payout(db, payout)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Falha ao transferir via Asaas")
    db.refresh(payout)
    return _to_response(payout)


@router.post("/{payout_id}/bloquear", response_model=PayoutResponse)
def block(
    payout_id: uuid.UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    payout = db.get(Payout, payout_id)
    if not payout:
        raise HTTPException(status_code=404, detail="Repasse não encontrado")
    payout.status = PayoutStatus.BLOQUEADO
    db.commit()
    db.refresh(payout)
    return _to_response(payout)


@router.get("/export")
def export_csv(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["studio", "semana", "bruto", "taxa_pct", "taxa", "liquido", "status"])
    for p in db.query(Payout).order_by(Payout.semana_inicio.desc()).all():
        w.writerow([
            p.studio.name if p.studio else "",
            p.semana_inicio.isoformat(),
            float(p.valor_bruto),
            float(p.taxa_admin_pct),
            float(p.taxa_admin_valor),
            float(p.valor_liquido),
            p.status.value,
        ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=repasses.csv"},
    )
