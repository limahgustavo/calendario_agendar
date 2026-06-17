import re
import uuid

from pydantic import BaseModel, Field, field_validator


class AvailabilityUpsert(BaseModel):
    ano: int = Field(..., ge=2024, le=2100)
    mes: int = Field(..., ge=1, le=12)
    dias_semana: list[int] = Field(default_factory=list)  # 0=segunda ... 6=domingo
    horarios: list[str] = Field(default_factory=list)  # 'HH:MM'

    @field_validator("dias_semana")
    @classmethod
    def validate_weekdays(cls, v: list[int]) -> list[int]:
        if any(d < 0 or d > 6 for d in v):
            raise ValueError("Dia da semana deve ser 0-6")
        return sorted(set(v))

    @field_validator("horarios")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        for t in v:
            if not re.match(r"^\d{2}:\d{2}$", t):
                raise ValueError(f"Horário inválido: {t}")
        return sorted(set(v))


class AvailabilityResponse(BaseModel):
    id: uuid.UUID
    studio_id: uuid.UUID
    ano: int
    mes: int
    dias_semana: list[int]
    horarios: list[str]

    model_config = {"from_attributes": True}


class CalendarSlot(BaseModel):
    date: str  # YYYY-MM-DD
    time_str: str  # HH:MM
    available: bool
