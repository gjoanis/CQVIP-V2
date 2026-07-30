from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_project_owner, verify_project_access
from app.models.enums import SystemType
from app.models.user import User
from app.services.system_service import SystemService

router = APIRouter(prefix="/systems", tags=["systems"])


class SystemIn(BaseModel):
    project_id: str
    name: str
    system_type: SystemType = SystemType.EQUIPMENT
    identifier: str = ""
    description: str = ""
    location: str = ""


class SystemOut(SystemIn):
    id: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[SystemOut])
def list_systems(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return SystemService(db).list_for_project(project_id)


@router.post("", response_model=SystemOut)
def create_system(payload: SystemIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    verify_project_access(payload.project_id, current_user, db)
    return SystemService(db).create(**payload.model_dump())


@router.get("/{system_id}", response_model=SystemOut)
def get_system(system_id: str, db: Session = Depends(get_db)):
    return SystemService(db).get(system_id)


@router.put("/{system_id}", response_model=SystemOut)
def update_system(system_id: str, payload: SystemIn, db: Session = Depends(get_db)):
    return SystemService(db).update(system_id, **payload.model_dump())


@router.delete("/{system_id}")
def delete_system(system_id: str, db: Session = Depends(get_db)):
    SystemService(db).delete(system_id)
    return {"deleted": system_id}
