import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_project_owner
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
def list_reports(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return ReportService(db).list_for_project(project_id)


@router.post("/generate", response_model=ReportOut)
def generate_report(
    generated_by_id: str | None = None, project_id: str = Depends(require_project_owner),
    db: Session = Depends(get_db),
):
    project = ProjectRepository(db).get_or_404(project_id)
    return generate_validation_summary_report(db, project, generated_by_id=generated_by_id)


@router.get("/{report_id}/download")
def download_report(report_id: str, project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    report = ReportService(db).get_in_project(project_id, report_id)
    if not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(
        report.file_path, filename=os.path.basename(report.file_path), media_type="text/markdown",
    )


class ReportContentOut(BaseModel):
    content: str


class ReportContentIn(BaseModel):
    content: str


@router.get("/{report_id}/content", response_model=ReportContentOut)
def get_report_content(
    report_id: str, project_id: str = Depends(require_project_owner), db: Session = Depends(get_db),
):
    service = ReportService(db)
    report = service.get_in_project(project_id, report_id)
    if not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not found on disk")
    return ReportContentOut(content=service.read_content(report))


@router.put("/{report_id}/content", response_model=ReportContentOut)
def update_report_content(
    payload: ReportContentIn, report_id: str, project_id: str = Depends(require_project_owner),
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    report = service.get_in_project(project_id, report_id)
    service.write_content(report, payload.content)
    return ReportContentOut(content=payload.content)
