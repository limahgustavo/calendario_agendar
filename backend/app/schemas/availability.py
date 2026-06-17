import re
from pydantic import BaseModel, Field, field_validator


class SlotCreate(BaseModel):
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    weekday: int = Field(..., ge=0, le=6)
    time_str: str

    @field_validator("time_str")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("Formato inválido. Use HH:MM")
        h, m = int(v[:2]), int(v[3:])
        if h > 23 or m > 59:
            raise ValueError("Hora inválida")
        return v


class SlotBulkCreate(BaseModel):
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    weekdays: list[int] = Field(..., min_length=1)
    times: list[str] = Field(..., min_length=1)

    @field_validator("weekdays")
    @classmethod
    def validate_weekdays(cls, v: list[int]) -> list[int]:
        if any(d < 0 or d > 6 for d in v):
            raise ValueError("Weekday deve ser 0-6")
        return v

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        for t in v:
            if not re.match(r"^\d{2}:\d{2}$", t):
                raise ValueError(f"Formato inválido: {t}")
        return v


class SlotResponse(BaseModel):
    id: int
    month_year: str
    weekday: int
    time_str: str

    model_config = {"from_attributes": True}


class CalendarSlotResponse(BaseModel):
    date: str        # YYYY-MM-DD
    time_str: str    # HH:MM
    available: bool
