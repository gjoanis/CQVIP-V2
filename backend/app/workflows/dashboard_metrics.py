"""Computes the portfolio-level Dashboard: every project, its overall completion
percentage, and counts of the entities it depends on (systems, documents,
requirements, risks, validation activities). This is deliberately lightweight/
deterministic (reuses the same readiness math as the per-project dashboard, no
AI calls) since it has to load fast for every project at once.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.document import Document
from app.models.project import Project
from app.models.system import System
from app.models.validation_activity import ValidationActivity
from app.workflows.project_readiness import compute_project_dashboard


def _count(db: Session, model, project_id: str) -> int:
    return db.execute(
        select(func.count()).select_from(model).where(model.project_id == project_id)
    ).scalar_one()


def compute_dashboard_metrics(db: Session) -> dict:
    projects = list(db.execute(select(Project)).scalars().all())
    clients_by_id = {c.id: c for c in db.execute(select(Client)).scalars().all()}

    project_rows = []
    total_open_risks = 0
    for project in projects:
        metrics = compute_project_dashboard(db, project.id)
        client = clients_by_id.get(project.client_id)
        total_open_risks += metrics["open_risks"]
        project_rows.append({
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "client_name": client.name if client else "—",
            "status": project.status.value,
            "completion_pct": metrics["lifecycle_readiness_pct"],
            "project_health": metrics["project_health"],
            "current_stage": metrics["current_stage"],
            "systems_count": _count(db, System, project.id),
            "documents_count": _count(db, Document, project.id),
            "requirements_count": metrics["total_requirements"],
            "open_risks": metrics["open_risks"],
            "validation_activities_count": _count(db, ValidationActivity, project.id),
        })

    return {
        "projects": project_rows,
        "total_projects": len(projects),
        "open_risks": total_open_risks,
    }
