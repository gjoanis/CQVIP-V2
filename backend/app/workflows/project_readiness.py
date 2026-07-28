"""Computes the project-scoped readiness metrics, gap analysis, and action queue
shown on the Dashboard: lifecycle readiness, Inspection Readiness Index (IRI),
5-phase breakdown, and derived per-requirement gaps.

These are deliberately deterministic/computed rather than AI-generated: the
values need to be instant and always in sync with the live data on every
dashboard load. Only the executive summary paragraph (app.ai.executive_summary)
is a real model call, since it's one call per load and benefits from natural
language variation.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RequirementPriority, RequirementStatus, ValidationStatus
from app.models.requirement import Requirement
from app.models.risk import Risk
from app.models.traceability import Traceability
from app.models.validation_activity import ValidationActivity

STAGE_NAMES = [
    "Planning & Requirements",
    "Design & Risk Assessment",
    "Execution",
    "Verification & Evidence Collection",
    "Completion & Release",
]

DOC_TYPE_LABELS = {
    "URS": "User Requirements Specification",
    "FS": "Functional Specification",
    "DS": "Design Specification",
    "HDS": "Hardware Design Specification",
    "SDS": "Software Design Specification",
    "FAT": "Factory Acceptance Test",
    "SAT": "Site Acceptance Test",
    "IQ": "Installation Qualification",
    "OQ": "Operational Qualification",
    "PQ": "Performance Qualification",
}


def _pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def compute_project_dashboard(db: Session, project_id: str) -> dict:
    requirements = list(db.execute(
        select(Requirement).where(Requirement.project_id == project_id)
    ).scalars().all())
    risks = list(db.execute(select(Risk).where(Risk.project_id == project_id)).scalars().all())
    activities = list(db.execute(
        select(ValidationActivity).where(ValidationActivity.project_id == project_id)
    ).scalars().all())
    protocol_linked_req_ids = set(db.execute(
        select(Traceability.requirement_id).where(
            Traceability.project_id == project_id, Traceability.protocol_id.is_not(None),
        )
    ).scalars().all())

    total_reqs = len(requirements)

    # Phase 1: how many requirements have moved past initial triage.
    phase1 = _pct(sum(1 for r in requirements if r.status != RequirementStatus.OPEN), total_reqs)
    # Phase 2: how many have had risk/design assessment run (AI Assessment populated).
    phase2 = _pct(sum(1 for r in requirements if r.risk), total_reqs)
    # Phase 3: how many have a protocol generated (execution started).
    phase3 = _pct(sum(1 for r in requirements if r.id in protocol_linked_req_ids), total_reqs)
    # Phase 4: how many are verified.
    phase4 = _pct(sum(1 for r in requirements if r.verified), total_reqs)
    # Phase 5: how many are fully closed out.
    phase5 = _pct(sum(1 for r in requirements if r.status == RequirementStatus.CLOSED), total_reqs)

    phase_readiness = [
        {"phase": 1, "label": "Requirements Readiness", "pct": phase1},
        {"phase": 2, "label": "Design & Risk Readiness", "pct": phase2},
        {"phase": 3, "label": "Execution Readiness", "pct": phase3},
        {"phase": 4, "label": "Verification & Evidence", "pct": phase4},
        {"phase": 5, "label": "Completion & Release", "pct": phase5},
    ]
    lifecycle_readiness = round(sum(p["pct"] for p in phase_readiness) / len(phase_readiness), 1)

    # Inspection Readiness Index: are the high-stakes items (critical/high priority)
    # actually verified, and is the audit trail (GMP references) populated?
    critical_high = [r for r in requirements if r.priority in (RequirementPriority.CRITICAL, RequirementPriority.HIGH)]
    critical_high_verified_pct = _pct(sum(1 for r in critical_high if r.verified), len(critical_high))
    gmp_reference_pct = _pct(sum(1 for r in requirements if r.gmp_reference), total_reqs)
    inspection_readiness_index = round((critical_high_verified_pct + gmp_reference_pct) / 2, 1)

    # Validation Execution Readiness: how much of the actual test EXECUTION
    # (validation activities, not just protocol generation) is complete.
    # Activities marked not-applicable are excluded from scope entirely --
    # they shouldn't count against readiness any more than they count toward it.
    in_scope_activities = [a for a in activities if a.status != ValidationStatus.NOT_APPLICABLE]
    execution_readiness = _pct(
        sum(1 for a in in_scope_activities if a.status == ValidationStatus.PASSED), len(in_scope_activities),
    )

    # Current stage: the earliest phase that isn't substantially complete yet.
    stage_index = next((i for i, p in enumerate(phase_readiness) if p["pct"] < 90), len(phase_readiness) - 1)
    current_stage = STAGE_NAMES[stage_index]

    if lifecycle_readiness < 40:
        project_health = "red"
    elif lifecycle_readiness < 75:
        project_health = "yellow"
    else:
        project_health = "green"

    critical_or_high_open = sum(
        1 for r in requirements
        if r.priority in (RequirementPriority.CRITICAL, RequirementPriority.HIGH) and not r.verified
    )
    awaiting_verification = sum(1 for r in requirements if not r.verified and r.status != RequirementStatus.NOT_APPLICABLE)

    return {
        "lifecycle_readiness_pct": lifecycle_readiness,
        "inspection_readiness_index_pct": inspection_readiness_index,
        "execution_readiness_pct": execution_readiness,
        "current_stage": current_stage,
        "project_health": project_health,
        "phase_readiness": phase_readiness,
        "total_requirements": total_reqs,
        "critical_or_high_open": critical_or_high_open,
        "awaiting_verification": awaiting_verification,
        "open_risks": sum(1 for r in risks if r.status.value != "closed"),
    }


def _doc_type_label(requirement: Requirement) -> str:
    if requirement.document and requirement.document.doc_type:
        return DOC_TYPE_LABELS.get(requirement.document.doc_type.upper(), requirement.document.doc_type)
    return "source specification"


def compute_gap_analysis(db: Session, project_id: str, current_stage: str) -> list[dict]:
    requirements = list(db.execute(
        select(Requirement).where(Requirement.project_id == project_id)
    ).scalars().all())

    rows = []
    for r in requirements:
        if r.status == RequirementStatus.NOT_APPLICABLE:
            gap, risk, recommendation = "None", "low", "Excluded from validation scope (not applicable)."
        elif r.verified:
            gap, risk, recommendation = "None", "low", "Requirement verified."
        else:
            gap = "Verification Evidence Missing"
            risk = "high" if r.priority in (RequirementPriority.CRITICAL, RequirementPriority.HIGH) else "medium"
            recommendation = (
                f"Complete verification within the {current_stage} stage and update the "
                f"{_doc_type_label(r)}."
            )
        rows.append({
            "requirement_id": r.id,
            "req_code": r.req_code,
            "title": r.title,
            "category": r.category,
            "priority": r.priority,
            "status": r.status,
            "gap": gap,
            "risk": risk,
            "recommendation": recommendation,
        })
    return rows


def compute_action_queue(db: Session, project_id: str, current_stage: str) -> list[dict]:
    from app.models.user import User

    gap_rows = [row for row in compute_gap_analysis(db, project_id, current_stage) if row["gap"] != "None"]
    priority_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gap_rows.sort(key=lambda row: priority_rank.get(row["priority"].value, 4))

    requirements_by_id = {
        r.id: r for r in db.execute(
            select(Requirement).where(Requirement.project_id == project_id)
        ).scalars().all()
    }
    users_by_id = {u.id: u for u in db.execute(select(User)).scalars().all()}

    queue = []
    for row in gap_rows:
        requirement = requirements_by_id[row["requirement_id"]]
        owner = users_by_id.get(requirement.assigned_to_id)
        queue.append({
            "priority": row["priority"],
            "requirement_id": requirement.id,
            "req_code": row["req_code"],
            "title": row["title"],
            "action_required": row["recommendation"],
            "owner_name": owner.full_name if owner else "Unassigned",
            "status": row["status"],
        })
    return queue
