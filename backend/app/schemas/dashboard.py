from pydantic import BaseModel

from app.schemas.appointment import AppointmentResponse


class StudioDashboard(BaseModel):
    proximos: list[AppointmentResponse]
    faturamento_mes_recebido: float
    faturamento_mes_a_receber: float
    total_mes: int
    confirmados_mes: int
    pendentes_count: int


class ReportMonth(BaseModel):
    mes: int
    recebido: float
    total: int
    realizados: int
    cancelados: int


class StudioReport(BaseModel):
    ano: int
    meses: list[ReportMonth]
    media_avaliacao: float | None
    total_avaliacoes: int
    servicos_top: list[dict]
