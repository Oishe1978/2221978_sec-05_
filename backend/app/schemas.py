from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]


class CaseBase(BaseModel):
    district: str = Field(min_length=2, max_length=60)
    report_date: date
    cases: int = Field(ge=0)
    deaths: int = Field(default=0, ge=0)
    recovered: int = Field(default=0, ge=0)
    severity: Severity = "low"


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    """All fields optional so the client can send only what changed."""

    district: str | None = Field(default=None, min_length=2, max_length=60)
    report_date: date | None = None
    cases: int | None = Field(default=None, ge=0)
    deaths: int | None = Field(default=None, ge=0)
    recovered: int | None = Field(default=None, ge=0)
    severity: Severity | None = None


class Case(CaseBase):
    id: UUID
    created_at: datetime