from datetime import date

from sqlalchemy.orm import Session

from app.models.enums import ProjectStatus
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.workflows.audit_logging import log_action


class ProjectLifecycleEngine:
    """Drives a project through planning -> active -> completed / cancelled."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)

    def activate(self, project_id: str, *, actor_user_id: str | None = None) -> Project:
        return self._transition(project_id, ProjectStatus.ACTIVE, actor_user_id)

    def hold(self, project_id: str, *, actor_user_id: str | None = None) -> Project:
        return self._transition(project_id, ProjectStatus.ON_HOLD, actor_user_id)

    def complete(self, project_id: str, *, actor_user_id: str | None = None) -> Project:
        project = self._transition(project_id, ProjectStatus.COMPLETED, actor_user_id)
        return self.repo.update(project, actual_end_date=date.today())

    def cancel(self, project_id: str, *, actor_user_id: str | None = None) -> Project:
        return self._transition(project_id, ProjectStatus.CANCELLED, actor_user_id)

    def _transition(self, project_id: str, status: ProjectStatus, actor_user_id: str | None) -> Project:
        project = self.repo.get_or_404(project_id)
        project = self.repo.update(project, status=status)
        log_action(
            self.db, user_id=actor_user_id, action=f"transition_to_{status.value}",
            entity_type="Project", entity_id=project.id,
        )
        return project
