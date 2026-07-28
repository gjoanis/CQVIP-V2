from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.enums import RiskSeverity, RiskStatus
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risks", tags=["risk-register"])


class RiskIn(BaseModel):
    project_id: str
    requirement_id: str | None = None
    owner_id: str | None = None
    title: str
    description: str = ""
    severity: RiskSeverity = RiskSeverity.MEDIUM
    likelihood: RiskSeverity = RiskSeverity.MEDIUM
    mitigation: str = ""
    status: RiskStatus = RiskStatus.OPEN


class RiskOut(RiskIn):
    id: str
    risk_score: int

    model_config = {"from_attributes": True}


@router.get("", response_model=list[RiskOut])
def list_risks(project_id: str, db: Session = Depends(get_db)):
    return RiskService(db).list_for_project(project_id)


@router.post("", response_model=RiskOut)
def create_risk(payload: RiskIn, db: Session = Depends(get_db)):
    return RiskService(db).create(**payload.model_dump())


@router.put("/{risk_id}", response_model=RiskOut)
def update_risk(risk_id: str, payload: RiskIn, db: Session = Depends(get_db)):
    return RiskService(db).update(risk_id, **payload.model_dump())
