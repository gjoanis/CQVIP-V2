from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository


class EvidenceService:
    def __init__(self, db: Session):
        self.repo = EvidenceRepository(db)

    def attach(self, **fields) -> Evidence:
        return self.repo.create(Evidence(**fields))
