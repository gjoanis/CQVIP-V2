from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.fmea_suggestion import FmeaSuggestion
from app.api.deps import get_current_user, get_db, require_fmea_owner, require_project_owner, verify_project_access
from app.models.enums import FmeaStatus
from app.models.user import User
from app.repositories.system_repository import SystemRepository
from app.services.fmea_service import FmeaService

router = APIRouter(prefix="/fmea", tags=["fmea"])


class FmeaAnalysisIn(BaseModel):
    project_id: str
    system_id: str
    title: str
    description: str = ""
    status: FmeaStatus = FmeaStatus.DRAFT


class FmeaAnalysisOut(FmeaAnalysisIn):
    id: str

    model_config = {"from_attributes": True}


class FmeaLineItemCreateIn(BaseModel):
    process_step: str
    order: int = 0


class FmeaLineItemUpdateIn(BaseModel):
    process_step: str | None = None
    potential_failure_mode: str | None = None
    potential_effect: str | None = None
    severity: int | None = None
    potential_cause: str | None = None
    occurrence: int | None = None
    current_controls: str | None = None
    detection: int | None = None
    recommended_action: str | None = None
    action_owner_id: str | None = None
    target_date: date | None = None
    action_taken: str | None = None
    resulting_severity: int | None = None
    resulting_occurrence: int | None = None
    resulting_detection: int | None = None
    order: int | None = None


class FmeaLineItemOut(BaseModel):
    id: str
    fmea_id: str
    order: int
    process_step: str
    potential_failure_mode: str
    potential_effect: str
    severity: int
    potential_cause: str
    occurrence: int
    current_controls: str
    detection: int
    rpn: int
    recommended_action: str
    action_owner_id: str | None
    target_date: date | None
    action_taken: str
    resulting_severity: int | None
    resulting_occurrence: int | None
    resulting_detection: int | None
    resulting_rpn: int | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[FmeaAnalysisOut])
def list_fmea(project_id: str = Depends(require_project_owner), db: Session = Depends(get_db)):
    return FmeaService(db).list_for_project(project_id)


@router.post("", response_model=FmeaAnalysisOut)
def create_fmea(
    payload: FmeaAnalysisIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    verify_project_access(payload.project_id, current_user, db)
    return FmeaService(db).create(**payload.model_dump())


@router.get("/{fmea_id}", response_model=FmeaAnalysisOut)
def get_fmea(fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db)):
    return FmeaService(db).get(fmea_id)


@router.put("/{fmea_id}", response_model=FmeaAnalysisOut)
def update_fmea(
    payload: FmeaAnalysisIn, fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db),
):
    return FmeaService(db).update(fmea_id, title=payload.title, description=payload.description, status=payload.status)


@router.delete("/{fmea_id}")
def delete_fmea(fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db)):
    FmeaService(db).delete(fmea_id)
    return {"deleted": fmea_id}


@router.get("/{fmea_id}/items", response_model=list[FmeaLineItemOut])
def list_items(fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db)):
    return FmeaService(db).list_items(fmea_id)


@router.post("/{fmea_id}/items", response_model=FmeaLineItemOut)
def create_item(
    payload: FmeaLineItemCreateIn, fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db),
):
    return FmeaService(db).create_item(fmea_id=fmea_id, **payload.model_dump())


@router.put("/{fmea_id}/items/{item_id}", response_model=FmeaLineItemOut)
def update_item(
    item_id: str, payload: FmeaLineItemUpdateIn,
    fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db),
):
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    return FmeaService(db).update_item(fmea_id, item_id, **fields)


@router.delete("/{fmea_id}/items/{item_id}")
def delete_item(item_id: str, fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db)):
    FmeaService(db).delete_item(fmea_id, item_id)
    return {"deleted": item_id}


@router.post("/{fmea_id}/items/{item_id}/ai-suggest", response_model=FmeaLineItemOut)
def ai_suggest_item(item_id: str, fmea_id: str = Depends(require_fmea_owner), db: Session = Depends(get_db)):
    """Runs the AI-suggested failure mode analysis (failure mode, effect, cause,
    controls, S/O/D ratings, recommended action) for one process step and
    returns it as a PREVIEW -- nothing is persisted here. The frontend shows it
    for review/edit; the user's own Accept action calls PUT to actually save it."""
    service = FmeaService(db)
    item = service.get_item_in_fmea(fmea_id, item_id)
    fmea = service.get(fmea_id)
    system = SystemRepository(db).get(fmea.system_id)
    result = FmeaSuggestion().run(process_step=item.process_step, system_name=system.name if system else "")
    preview = FmeaLineItemOut.model_validate(item)
    for key, value in result.items():
        setattr(preview, key, value)
    preview.rpn = preview.severity * preview.occurrence * preview.detection
    return preview
