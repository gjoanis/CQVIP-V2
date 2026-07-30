from sqlalchemy.orm import Session

from app.models.system import System
from app.repositories.system_repository import SystemRepository


class SystemService:
    def __init__(self, db: Session):
        self.repo = SystemRepository(db)

    def get(self, system_id: str) -> System:
        return self.repo.get_or_404(system_id)

    def list_for_project(self, project_id: str) -> list[System]:
        return self.repo.list_for_project(project_id)

    def create(self, **fields) -> System:
        return self.repo.create(System(**fields))

    def update(self, system_id: str, **fields) -> System:
        return self.repo.update(self.get(system_id), **fields)

    def delete(self, system_id: str) -> None:
        self.repo.delete(self.get(system_id))
