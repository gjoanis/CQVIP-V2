from sqlalchemy import select
from app.models.requirement import Requirement
from app.repositories.base import BaseRepository


class RequirementRepository(BaseRepository[Requirement]):
    model = Requirement

    def list_for_project(self, project_id: str):
        stmt = select(self.model).where(self.model.project_id == project_id)
        return list(self.db.execute(stmt).scalars().all())
