import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.requirement_assessment import RequirementAssessment
from app.api.deps import get_db
from app.config import get_settings
from app.models.attachment import Attachment
from app.models.enums import RequirementDisposition, RequirementPriority, RequirementStatus
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.requirement_repository import RequirementRepository
from app.services.requirement_service import RequirementService
from app.workflows.protocol_generation import generate_protocol_for_requirement

router = APIRouter(prefix="/requirements", tags=["requirements"])
settings = get_settings()


class RequirementIn(BaseModel):
    project_id: str
    document_id: str | None = None
    system_id: str | None = None
    req_code: str
    title: str
    description: str = ""
    category: str = ""
    priority: RequirementPriority = RequirementPriority.MEDIUM
    status: RequirementStatus = RequirementStatus.OPEN
    source: str = ""


class RequirementOut(BaseModel):
    id: str
    project_id: str
    document_id: str | None
    system_id: str | None
    req_code: str
    title: str
    description: str
    category: str
    priority: RequirementPriority
    status: RequirementStatus
    source: str
    disposition: RequirementDisposition
    assigned_to_id: str | None
    assigned_date: datetime | None
    review_date: datetime | None
    closed_date: datetime | None
    verified: bool
    risk: str
    gmp_reference: str
    acceptance_criteria: str
    suggested_test: str
    protocol_section: str
    verification_type: str

    model_config = {"from_attributes": True}


class ProtocolOut(BaseModel):
    id: str
    title: str
    protocol_number: str
    version: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[RequirementOut])
def list_requirements(project_id: str, db: Session = Depends(get_db)):
    return RequirementService(db).list_for_project(project_id)


@router.get("/{requirement_id}", response_model=RequirementOut)
def get_requirement(requirement_id: str, db: Session = Depends(get_db)):
    return RequirementService(db).get(requirement_id)


@router.post("", response_model=RequirementOut)
def create_requirement(payload: RequirementIn, db: Session = Depends(get_db)):
    return RequirementService(db).create(**payload.model_dump())


@router.put("/{requirement_id}", response_model=RequirementOut)
def update_requirement(requirement_id: str, payload: RequirementIn, db: Session = Depends(get_db)):
    return RequirementService(db).update(requirement_id, **payload.model_dump())


class StatusIn(BaseModel):
    status: RequirementStatus


@router.patch("/{requirement_id}/status", response_model=RequirementOut)
def set_status(requirement_id: str, payload: StatusIn, db: Session = Depends(get_db)):
    """Quick status change from the inline dropdown in the Requirements list."""
    repo = RequirementRepository(db)
    return repo.update(repo.get_or_404(requirement_id), status=payload.status)


class SystemLinkIn(BaseModel):
    system_id: str | None


@router.patch("/{requirement_id}/system", response_model=RequirementOut)
def set_system(requirement_id: str, payload: SystemLinkIn, db: Session = Depends(get_db)):
    """Set or clear which System/Process this requirement traces to."""
    repo = RequirementRepository(db)
    return repo.update(repo.get_or_404(requirement_id), system_id=payload.system_id)


class AssignOwnerIn(BaseModel):
    user_id: str


@router.post("/{requirement_id}/assign-owner", response_model=RequirementOut)
def assign_owner(requirement_id: str, payload: AssignOwnerIn, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return repo.update(
        req,
        assigned_to_id=payload.user_id,
        assigned_date=datetime.now(timezone.utc),
        status=RequirementStatus.IN_PROGRESS,
    )


@router.post("/{requirement_id}/mark-na", response_model=RequirementOut)
def mark_na(requirement_id: str, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return repo.update(
        req, disposition=RequirementDisposition.NOT_APPLICABLE, status=RequirementStatus.NOT_APPLICABLE,
    )


@router.post("/{requirement_id}/mark-under-review", response_model=RequirementOut)
def mark_under_review(requirement_id: str, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return repo.update(req, status=RequirementStatus.UNDER_REVIEW, review_date=datetime.now(timezone.utc))


@router.post("/{requirement_id}/verify", response_model=RequirementOut)
def verify_requirement(requirement_id: str, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return repo.update(req, verified=True, status=RequirementStatus.VERIFIED)


@router.post("/{requirement_id}/close", response_model=RequirementOut)
def close_requirement(requirement_id: str, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return repo.update(req, status=RequirementStatus.CLOSED, closed_date=datetime.now(timezone.utc))


@router.post("/{requirement_id}/assess", response_model=RequirementOut)
def assess_requirement(requirement_id: str, db: Session = Depends(get_db)):
    """Runs the AI Assessment (risk, GMP reference, acceptance criteria, suggested
    test, protocol section, verification type) and persists the result."""
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    result = RequirementAssessment().run(title=req.title, description=req.description, category=req.category)
    return repo.update(
        req,
        risk=result.get("risk", ""),
        gmp_reference=result.get("gmp_reference", ""),
        acceptance_criteria=result.get("acceptance_criteria", ""),
        suggested_test=result.get("suggested_test", ""),
        protocol_section=result.get("protocol_section", ""),
        verification_type=result.get("verification_type", ""),
    )


@router.post("/{requirement_id}/generate-protocol", response_model=ProtocolOut)
def generate_protocol(requirement_id: str, db: Session = Depends(get_db)):
    repo = RequirementRepository(db)
    req = repo.get_or_404(requirement_id)
    return generate_protocol_for_requirement(db, req)


class AttachmentOut(BaseModel):
    id: str
    file_name: str
    document_type: str
    content_type: str
    uploaded_by_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/{requirement_id}/attachments", response_model=list[AttachmentOut])
def list_attachments(requirement_id: str, db: Session = Depends(get_db)):
    return AttachmentRepository(db).list_for_entity("Requirement", requirement_id)


@router.post("/{requirement_id}/attachments", response_model=AttachmentOut)
async def upload_attachment(
    requirement_id: str, document_type: str, file: UploadFile,
    uploaded_by_id: str | None = None, db: Session = Depends(get_db),
):
    repo = RequirementRepository(db)
    repo.get_or_404(requirement_id)  # 404s if the requirement doesn't exist

    dest_dir = os.path.join(settings.storage_root, "attachments", "requirements", requirement_id)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file.filename)
    with open(dest_path, "wb") as out:
        out.write(await file.read())

    return AttachmentRepository(db).create(Attachment(
        entity_type="Requirement",
        entity_id=requirement_id,
        file_name=file.filename,
        file_path=dest_path,
        content_type=file.content_type or "",
        document_type=document_type,
        uploaded_by_id=uploaded_by_id,
    ))
