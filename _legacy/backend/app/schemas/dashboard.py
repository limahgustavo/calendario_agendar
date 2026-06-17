from pydantic import BaseModel


class RevenueSummary(BaseModel):
    month_year: str
    total_appointments: int
    confirmed_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    revenue_confirmed: float   # 50% recebidos
    revenue_pending: float     # 50% a receber no local


class DashboardSummary(BaseModel):
    today_appointments: int
    week_appointments: int
    current_month: RevenueSummary
    upcoming: list[dict]
