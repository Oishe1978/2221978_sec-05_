from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.repository import InMemoryCaseRepository, get_repository
from app.schemas import Case, CaseCreate, CaseUpdate, Severity

router = APIRouter(prefix="/api/v1", tags=["cases"])

Repo = Annotated[InMemoryCaseRepository, Depends(get_repository)]


@router.get("/cases", response_model=list[Case])
def list_cases(
    repo: Repo,
    district: str | None = None,
    severity: Severity | None = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> list[Case]:
    return repo.list(district, severity, date_from, date_to)


@router.get("/cases/{case_id}", response_model=Case)
def get_case(case_id: UUID, repo: Repo) -> Case:
    case = repo.get(case_id)
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case report not found")
    return case


@router.post("/cases", response_model=Case, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, repo: Repo) -> Case:
    return repo.create(payload)


@router.patch("/cases/{case_id}", response_model=Case)
def update_case(case_id: UUID, payload: CaseUpdate, repo: Repo) -> Case:
    case = repo.update(case_id, payload)
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case report not found")
    return case


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: UUID, repo: Repo) -> Response:
    if not repo.delete(case_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case report not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dengue-stats")
def dengue_stats(repo: Repo) -> dict[str, int]:
    """Summary for the dashboard cards (matches the TDD endpoint)."""
    items = repo.list()
    total = sum(c.cases for c in items)
    deaths = sum(c.deaths for c in items)
    recovered = sum(c.recovered for c in items)
    return {
        "total_cases": total,
        "active_cases": max(total - recovered - deaths, 0),
        "recovered": recovered,
        "deaths": deaths,
    }