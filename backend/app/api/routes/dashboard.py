from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.workflows.dashboard_metrics import compute_dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class PortfolioProjectOut(BaseModel):
    id: str
    code: str
    name: str
    client_name: str
    status: str
    completion_pct: float
    project_health: str
    current_stage: str
    systems_count: int
    documents_count: int
    requirements_count: int
    open_risks: int
    validation_activities_count: int


class PortfolioDashboardOut(BaseModel):
    projects: list[PortfolioProjectOut]
    total_projects: int
    open_risks: int


@router.get("", response_model=PortfolioDashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    return compute_dashboard_metrics(db)
