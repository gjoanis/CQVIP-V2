from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_project_owner, verify_project_access
from app.models.enums import ValidationActivityType, ValidationStatus
from app.models.user import User
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/validation-activities", tags=["validation-activities"])


class ValidationActivityIn(BaseModel):
    project_id: str
    owner_id: str | None = None
    name: str
    activity_type: ValidationActivityType = ValidationActivityType.OTHER
    status: ValidationStatus = ValidationStatus.NOT_STARTED
    planned_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None


class ValidationActivityUpdateIn(BaseModel):
    name: str | None = None
    owner_id: str | None = None
    activity_type: ValidationActivityType | None = None
    status: ValidationStatus | None = None
    planned_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None


class ValidationActivityOut(ValidationActivityIn):
    id: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ValidationActivityOut])
def list_activities(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return ValidationService(db).list_for_project(project_id)


@router.post("", response_model=ValidationActivityOut)
def create_activity(
    payload: ValidationActivityIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    verify_project_access(payload.project_id, current_user, db)
    return ValidationService(db).create(**payload.model_dump())


@router.put("/{activity_id}", response_model=ValidationActivityOut)
def update_activity(activity_id: str, payload: ValidationActivityUpdateIn, db: Session = Depends(get_db)):
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    return ValidationService(db).update(activity_id, **fields)


@router.post("/seed-standard-phases", response_model=list[ValidationActivityOut])
def seed_standard_phases(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return ValidationService(db).seed_standard_phases(project_id)
