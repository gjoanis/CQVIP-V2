from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import SystemType
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
def list_systems(project_id: str, db: Session = Depends(get_db)):
    return SystemService(db).list_for_project(project_id)


@router.post("", response_model=SystemOut)
def create_system(payload: SystemIn, db: Session = Depends(get_db)):
    return SystemService(db).create(**payload.model_dump())


@router.get("/{system_id}", response_model=SystemOut)
def get_system(system_id: str, db: Session = Depends(get_db)):
    return SystemService(db).get(system_id)


@router.put("/{system_id}", response_model=SystemOut)
def update_system(system_id: str, payload: SystemIn, db: Session = Depends(get_db)):
    return SystemService(db).update(system_id, **payload.model_dump())
