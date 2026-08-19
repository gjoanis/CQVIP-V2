from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.workflows.dashboard_metrics import compute_dashboard_metrics
from app.workflows.portfolio_trends import compute_leaderboard, compute_portfolio_trends

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
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return compute_dashboard_metrics(db, current_user.id)


class TrendPointOut(BaseModel):
    date: str
    requirements_total: int
    requirements_verified: int
    lifecycle_readiness_pct: float
    open_risks: int


class ProjectTrendOut(BaseModel):
    id: str
    code: str
    name: str
    points: list[TrendPointOut]


class PortfolioTrendsOut(BaseModel):
    weeks: int
    projects: list[ProjectTrendOut]


@router.get("/trends", response_model=PortfolioTrendsOut)
def get_trends(
    weeks: int = 12, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    return compute_portfolio_trends(db, current_user.id, weeks=weeks)


class LeaderboardRowOut(BaseModel):
    id: str
    code: str
    name: str
    requirement_count: int
    requirement_verified_count: int
    requirement_verification_rate_pct: float
    avg_requirement_verification_days: float | None
    risk_count: int
    closed_risk_count: int
    avg_risk_closure_days: float | None


class LeaderboardOut(BaseModel):
    projects: list[LeaderboardRowOut]


@router.get("/leaderboard", response_model=LeaderboardOut)
def get_leaderboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return compute_leaderboard(db, current_user.id)
