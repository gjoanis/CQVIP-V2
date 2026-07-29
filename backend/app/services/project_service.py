from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.workflows.audit_logging import log_action


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)

    def get(self, project_id: str) -> Project:
        return self.repo.get_or_404(project_id)

    def list_all(self, offset: int = 0, limit: int = 100) -> list[Project]:
        return self.repo.list_all(offset=offset, limit=limit)

    def list_for_client(self, client_id: str) -> list[Project]:
        return self.repo.list_for_client(client_id)

    def list_for_owner(self, owner_id: str, client_id: str | None = None) -> list[Project]:
        return self.repo.list_for_owner(owner_id, client_id)

    def create(self, *, actor_user_id: str | None = None, **fields) -> Project:
        project = self.repo.create(Project(**fields))
        log_action(self.db, user_id=actor_user_id, action="create", entity_type="Project", entity_id=project.id)
        return project

    def update(self, project_id: str, *, actor_user_id: str | None = None, **fields) -> Project:
        project = self.repo.update(self.get(project_id), **fields)
        log_action(self.db, user_id=actor_user_id, action="update", entity_type="Project", entity_id=project.id)
        return project
