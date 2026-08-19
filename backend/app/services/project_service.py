from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.workflows.audit_logging import log_action
from app.workflows.project_reset import reset_project


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

    def delete(self, project_id: str, *, actor_user_id: str | None = None) -> dict:
        """Wipes everything inside the project, then deletes the project
        itself. If the project's client has no other projects left, deletes
        the client too, so an orphaned client record doesn't linger."""
        project = self.get(project_id)
        client_id = project.client_id
        counts = reset_project(self.db, project_id)
        self.db.delete(project)
        self.db.commit()

        remaining_for_client = self.db.execute(
            select(Project.id).where(Project.client_id == client_id)
        ).first()
        client_deleted = False
        if remaining_for_client is None:
            client = self.db.get(Client, client_id)
            if client is not None:
                self.db.delete(client)
                self.db.commit()
                client_deleted = True

        log_action(
            self.db, user_id=actor_user_id, action="delete", entity_type="Project", entity_id=project_id,
            details={**counts, "client_deleted": client_deleted},
        )
        return {**counts, "client_deleted": client_deleted}
