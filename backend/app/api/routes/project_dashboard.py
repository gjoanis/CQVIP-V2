from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.executive_summary import ExecutiveSummary
from app.api.deps import get_db, require_project_owner
from app.models.enums import RequirementPriority, RequirementStatus
from app.workflows.project_readiness import (
    compute_action_queue,
    compute_gap_analysis,
    compute_project_dashboard,
)

router = APIRouter(prefix="/projects/{project_id}/dashboard", tags=["project-dashboard"])


class PhaseReadiness(BaseModel):
    phase: int
    label: str
    pct: float


class ProjectDashboardOut(BaseModel):
    lifecycle_readiness_pct: float
    inspection_readiness_index_pct: float
    execution_readiness_pct: float
    current_stage: str
    project_health: str
    phase_readiness: list[PhaseReadiness]
    total_requirements: int
    critical_or_high_open: int
    awaiting_verification: int
    open_risks: int
    executive_summary: str


class GapRowOut(BaseModel):
    requirement_id: str
    req_code: str
    title: str
    category: str
    priority: RequirementPriority
    status: RequirementStatus
    gap: str
    risk: str
    recommendation: str


class ActionQueueRowOut(BaseModel):
    priority: RequirementPriority
    requirement_id: str
    req_code: str
    title: str
    action_required: str
    owner_name: str
    status: RequirementStatus


@router.get("", response_model=ProjectDashboardOut)
def get_project_dashboard(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    metrics = compute_project_dashboard(db, project_id)
    summary = ExecutiveSummary().run(
        lifecycle_readiness_pct=metrics["lifecycle_readiness_pct"],
        inspection_readiness_index_pct=metrics["inspection_readiness_index_pct"],
        current_stage=metrics["current_stage"],
        project_health=metrics["project_health"],
        total_requirements=metrics["total_requirements"],
        critical_or_high_open=metrics["critical_or_high_open"],
        awaiting_verification=metrics["awaiting_verification"],
        open_risks=metrics["open_risks"],
    )
    return {**metrics, "executive_summary": summary}


@router.get("/gap-analysis", response_model=list[GapRowOut])
def get_gap_analysis(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    metrics = compute_project_dashboard(db, project_id)
    return compute_gap_analysis(db, project_id, metrics["current_stage"])


@router.get("/action-queue", response_model=list[ActionQueueRowOut])
def get_action_queue(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    metrics = compute_project_dashboard(db, project_id)
    return compute_action_queue(db, project_id, metrics["current_stage"])
