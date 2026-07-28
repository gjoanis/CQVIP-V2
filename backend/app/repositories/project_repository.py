from sqlalchemy import select
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    def list_for_client(self, client_id: str):
        stmt = select(self.model).where(self.model.client_id == client_id)
        return list(self.db.execute(stmt).scalars().all())
