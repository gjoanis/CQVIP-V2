from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.protocol import Protocol
from app.models.requirement import Requirement
from app.models.test_step import TestStep
from app.services.traceability_service import TraceabilityService

router = APIRouter(prefix="/projects/{project_id}/traceability", tags=["traceability"])


class TraceabilityRowOut(BaseModel):
    id: str
    requirement_id: str
    req_code: str
    requirement_title: str
    protocol_id: str | None
    protocol_number: str | None
    protocol_title: str | None
    test_step_id: str | None
    test_step_description: str | None
    coverage_status: str


@router.get("/matrix", response_model=list[TraceabilityRowOut])
def get_matrix(project_id: str, db: Session = Depends(get_db)):
    links = TraceabilityService(db).matrix_for_project(project_id)

    requirement_ids = {link.requirement_id for link in links}
    protocol_ids = {link.protocol_id for link in links if link.protocol_id}
    test_step_ids = {link.test_step_id for link in links if link.test_step_id}

    requirements = {
        r.id: r for r in db.execute(select(Requirement).where(Requirement.id.in_(requirement_ids))).scalars()
    } if requirement_ids else {}
    protocols = {
        p.id: p for p in db.execute(select(Protocol).where(Protocol.id.in_(protocol_ids))).scalars()
    } if protocol_ids else {}
    test_steps = {
        t.id: t for t in db.execute(select(TestStep).where(TestStep.id.in_(test_step_ids))).scalars()
    } if test_step_ids else {}

    rows = []
    for link in links:
        requirement = requirements.get(link.requirement_id)
        protocol = protocols.get(link.protocol_id) if link.protocol_id else None
        test_step = test_steps.get(link.test_step_id) if link.test_step_id else None
        rows.append(TraceabilityRowOut(
            id=link.id,
            requirement_id=link.requirement_id,
            req_code=requirement.req_code if requirement else link.requirement_id,
            requirement_title=requirement.title if requirement else "",
            protocol_id=link.protocol_id,
            protocol_number=protocol.protocol_number if protocol else None,
            protocol_title=protocol.title if protocol else None,
            test_step_id=link.test_step_id,
            test_step_description=test_step.description if test_step else None,
            coverage_status=link.coverage_status,
        ))
    return rows


@router.get("/coverage")
def get_coverage(project_id: str, db: Session = Depends(get_db)):
    return TraceabilityService(db).coverage_summary(project_id)
