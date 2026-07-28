from sqlalchemy import select

from app.models.system import System
from app.repositories.base import BaseRepository


class SystemRepository(BaseRepository[System]):
    model = System

    def list_for_project(self, project_id: str) -> list[System]:
        stmt = select(self.model).where(self.model.project_id == project_id)
        return list(self.db.execute(stmt).scalars().all())
