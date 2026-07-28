from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.repositories.risk_repository import RiskRepository

_SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}


class RiskService:
    def __init__(self, db: Session):
        self.repo = RiskRepository(db)

    def list_for_project(self, project_id: str) -> list[Risk]:
        return [r for r in self.repo.list_all(limit=1000) if r.project_id == project_id]

    def create(self, **fields) -> Risk:
        risk = Risk(**fields)
        risk.risk_score = self._score(risk)
        return self.repo.create(risk)

    def update(self, risk_id: str, **fields) -> Risk:
        risk = self.repo.update(self.repo.get_or_404(risk_id), **fields)
        risk.risk_score = self._score(risk)
        return self.repo.update(risk, risk_score=risk.risk_score)

    @staticmethod
    def _score(risk: Risk) -> int:
        sev = _SEVERITY_WEIGHT.get(getattr(risk.severity, "value", risk.severity), 2)
        like = _SEVERITY_WEIGHT.get(getattr(risk.likelihood, "value", risk.likelihood), 2)
        return sev * like
