from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from app.schemas import Case, CaseCreate, CaseUpdate


class InMemoryCaseRepository:
    """Temporary storage. Will be replaced by a Supabase-backed class
    with the same methods, so the routes never change."""

    def __init__(self) -> None:
        self._items: dict[UUID, Case] = {}
        self._seed()

    def _seed(self) -> None:
        samples = [
            ("Dhaka", date(2026, 10, 28), 320, 4, 290, "high"),
            ("Chattogram", date(2026, 10, 28), 85, 1, 70, "medium"),
            ("Khulna", date(2026, 10, 29), 40, 0, 38, "low"),
            ("Rajshahi", date(2026, 10, 29), 22, 0, 20, "low"),
        ]
        for district, d, cases, deaths, rec, sev in samples:
            self.create(CaseCreate(district=district, report_date=d, cases=cases,
                                   deaths=deaths, recovered=rec, severity=sev))

    def list(self, district: str | None = None, severity: str | None = None,
             date_from: date | None = None, date_to: date | None = None) -> list[Case]:
        items = list(self._items.values())
        if district:
            items = [c for c in items if c.district.lower() == district.lower()]
        if severity:
            items = [c for c in items if c.severity == severity]
        if date_from:
            items = [c for c in items if c.report_date >= date_from]
        if date_to:
            items = [c for c in items if c.report_date <= date_to]
        return sorted(items, key=lambda c: c.report_date, reverse=True)

    def get(self, case_id: UUID) -> Case | None:
        return self._items.get(case_id)

    def create(self, payload: CaseCreate) -> Case:
        case = Case(id=uuid4(), created_at=datetime.now(timezone.utc),
                    **payload.model_dump())
        self._items[case.id] = case
        return case

    def update(self, case_id: UUID, payload: CaseUpdate) -> Case | None:
        existing = self._items.get(case_id)
        if existing is None:
            return None
        updated = existing.model_copy(update=payload.model_dump(exclude_unset=True))
        self._items[case_id] = updated
        return updated

    def delete(self, case_id: UUID) -> bool:
        return self._items.pop(case_id, None) is not None


_repo = InMemoryCaseRepository()


def get_repository() -> InMemoryCaseRepository:
    return _repo