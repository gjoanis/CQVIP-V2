from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import ProjectStatus
from app.services.project_service import ProjectService

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
def list_projects(client_id: str | None = None, db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.list_for_client(client_id) if client_id else service.list_all()


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectIn, db: Session = Depends(get_db)):
    return ProjectService(db).create(**payload.model_dump())


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return ProjectService(db).get(project_id)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, payload: ProjectIn, db: Session = Depends(get_db)):
    return ProjectService(db).update(project_id, **payload.model_dump())
