"""Wipes every piece of data inside a project (requirements, documents,
systems, FMEAs, protocols, validation activities, risks, and the handful of
lesser-used planning tables) while keeping the Project row itself -- so a
project can be restarted from a clean slate without losing its name, client,
or dates. Deletions run in dependency order so nothing violates a foreign key
along the way.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.capa import CAPA
from app.models.deadline import Deadline
from app.models.deviation import Deviation
from app.models.document import Document
from app.models.fmea import FmeaAnalysis, FmeaLineItem
from app.models.milestone import Milestone
from app.models.project_node import ProjectNode
from app.models.project_phase import ProjectPhase
from app.models.protocol import Protocol
from app.models.report import Report
from app.models.risk import Risk
from app.models.system import System
from app.models.test_step import TestStep
from app.models.validation_activity import ValidationActivity
from app.services.document_service import DocumentService
from app.services.requirement_service import RequirementService


def reset_project(db: Session, project_id: str) -> dict:
    counts: dict[str, int] = {}

    def delete_all(model, **filters) -> int:
        stmt = select(model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(model, key) == value)
        rows = list(db.execute(stmt).scalars())
        for row in rows:
            db.delete(row)
        db.commit()
        return len(rows)

    fmea_ids = list(db.execute(select(FmeaAnalysis.id).where(FmeaAnalysis.project_id == project_id)).scalars())
    counts["fmea_line_items"] = sum(delete_all(FmeaLineItem, fmea_id=fid) for fid in fmea_ids)
    counts["fmea_analyses"] = delete_all(FmeaAnalysis, project_id=project_id)

    counts["requirements"] = RequirementService(db).delete_for_project(project_id)
    counts["risks"] = delete_all(Risk, project_id=project_id)

    counts["capas"] = delete_all(CAPA, project_id=project_id)
    counts["deviations"] = delete_all(Deviation, project_id=project_id)
    counts["deadlines"] = delete_all(Deadline, project_id=project_id)
    counts["milestones"] = delete_all(Milestone, project_id=project_id)
    counts["project_phases"] = delete_all(ProjectPhase, project_id=project_id)
    counts["reports"] = delete_all(Report, project_id=project_id)

    # ProjectNode is self-referential (parent_id -> project_nodes.id); delete
    # leaf nodes repeatedly until none remain rather than assuming a depth.
    node_deletes = 0
    for _ in range(20):
        leaf_ids = list(db.execute(
            select(ProjectNode.id).where(
                ProjectNode.project_id == project_id,
                ~ProjectNode.id.in_(
                    select(ProjectNode.parent_id).where(ProjectNode.parent_id.is_not(None))
                ),
            )
        ).scalars())
        if not leaf_ids:
            break
        for node_id in leaf_ids:
            db.delete(db.get(ProjectNode, node_id))
        db.commit()
        node_deletes += len(leaf_ids)
    counts["project_nodes"] = node_deletes

    activity_ids = list(
        db.execute(select(ValidationActivity.id).where(ValidationActivity.project_id == project_id)).scalars()
    )
    protocol_ids = list(
        db.execute(select(Protocol.id).where(Protocol.validation_activity_id.in_(activity_ids))).scalars()
    ) if activity_ids else []
    counts["test_steps"] = sum(delete_all(TestStep, protocol_id=pid) for pid in protocol_ids)
    counts["protocols"] = sum(delete_all(Protocol, validation_activity_id=aid) for aid in activity_ids)
    counts["validation_activities"] = delete_all(ValidationActivity, project_id=project_id)

    document_service = DocumentService(db)
    document_ids = list(db.execute(select(Document.id).where(Document.project_id == project_id)).scalars())
    for document_id in document_ids:
        document_service.delete(document_id)
    counts["documents"] = len(document_ids)

    counts["systems"] = delete_all(System, project_id=project_id)

    return counts
