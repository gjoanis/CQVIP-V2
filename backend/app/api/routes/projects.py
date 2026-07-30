from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_project_owner
from app.models.enums import ProjectStatus
from app.models.user import User
from app.services.project_service import ProjectService
from app.workflows.audit_logging import log_action
from app.workflows.project_reset import reset_project

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectIn(BaseModel):
    client_id: str
    name: str
    code: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: date | None = None
    target_end_date: date | None = None


class ProjectOut(ProjectIn):
    id: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ProjectOut])
def list_projects(
    client_id: str | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    return ProjectService(db).list_for_owner(current_user.id, client_id)


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    return ProjectService(db).create(**payload.model_dump(), owner_id=current_user.id, actor_user_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return ProjectService(db).get(project_id)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    payload: ProjectIn, project_id: str = Depends(require_project_owner), db: Session = Depends(get_db),
):
    return ProjectService(db).update(project_id, **payload.model_dump())


@router.post("/{project_id}/reset")
def reset_project_data(
    project_id: str = Depends(require_project_owner),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Wipes every requirement, document, system, FMEA, protocol, validation
    activity, and related record inside the project, keeping the project
    itself (name/client/dates) so it can be started fresh."""
    counts = reset_project(db, project_id)
    log_action(db, user_id=current_user.id, action="reset", entity_type="Project", entity_id=project_id, details=counts)
    return {"project_id": project_id, "deleted": counts}
