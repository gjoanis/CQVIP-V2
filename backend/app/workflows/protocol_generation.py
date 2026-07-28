import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.protocol_generation import ProtocolGeneration
from app.models.enums import ValidationActivityType
from app.models.protocol import Protocol
from app.models.requirement import Requirement
from app.models.test_step import TestStep
from app.models.traceability import Traceability
from app.models.validation_activity import ValidationActivity


def _resolve_activity_type(verification_type: str) -> ValidationActivityType:
    try:
        return ValidationActivityType[verification_type.upper()]
    except KeyError:
        return ValidationActivityType.OTHER


def _get_or_create_activity(db: Session, requirement: Requirement) -> ValidationActivity:
    activity_type = _resolve_activity_type(requirement.verification_type or "other")
    existing = db.execute(
        select(ValidationActivity).where(
            ValidationActivity.project_id == requirement.project_id,
            ValidationActivity.activity_type == activity_type,
        )
    ).scalars().first()
    if existing:
        return existing
    activity = ValidationActivity(
        project_id=requirement.project_id,
        name=f"{activity_type.value.upper()} Activities",
        activity_type=activity_type,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def generate_protocol_for_requirement(db: Session, requirement: Requirement) -> Protocol:
    """Drafts AI test steps for `requirement` and files them under a Protocol,
    creating (or reusing) a ValidationActivity for its verification type, and
    links the requirement to the protocol via a Traceability row.
    """
    activity = _get_or_create_activity(db, requirement)

    protocol = Protocol(
        validation_activity_id=activity.id,
        title=f"Protocol for {requirement.req_code}: {requirement.title}",
        protocol_number=f"PROT-{requirement.req_code}-{uuid.uuid4().hex[:6].upper()}",
    )
    db.add(protocol)
    db.commit()
    db.refresh(protocol)

    steps = ProtocolGeneration().run(
        requirement_title=requirement.title,
        requirement_description=requirement.description,
        acceptance_criteria=requirement.acceptance_criteria,
    )
    for i, step in enumerate(steps, start=1):
        db.add(TestStep(
            protocol_id=protocol.id,
            step_number=i,
            description=step.get("description", ""),
            expected_result=step.get("expected_result", ""),
        ))

    db.add(Traceability(
        project_id=requirement.project_id,
        requirement_id=requirement.id,
        protocol_id=protocol.id,
        coverage_status="covered",
    ))
    db.commit()
    db.refresh(protocol)
    return protocol
