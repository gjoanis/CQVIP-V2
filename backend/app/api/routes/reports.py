import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.project_repository import ProjectRepository
from app.services.report_service import ReportService
from app.workflows.report_generation import generate_validation_summary_report

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["reports"])


class ReportOut(BaseModel):
    id: str
    project_id: str
    generated_by_id: str | None
    report_type: str
    title: str
    file_path: str
    generated_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ReportOut])
def list_reports(project_id: str, db: Session = Depends(get_db)):
    return ReportService(db).list_for_project(project_id)


@router.post("/generate", response_model=ReportOut)
def generate_report(project_id: str, generated_by_id: str | None = None, db: Session = Depends(get_db)):
    project = ProjectRepository(db).get_or_404(project_id)
    return generate_validation_summary_report(db, project, generated_by_id=generated_by_id)


@router.get("/{report_id}/download")
def download_report(project_id: str, report_id: str, db: Session = Depends(get_db)):
    report = ReportService(db).get(report_id)
    if not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(
        report.file_path, filename=os.path.basename(report.file_path), media_type="text/markdown",
    )
