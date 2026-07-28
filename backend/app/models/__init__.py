"""Import every model here so Base.metadata / Alembic autogenerate see them all."""

from app.models.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.client import Client  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.project_phase import ProjectPhase  # noqa: F401
from app.models.milestone import Milestone  # noqa: F401
from app.models.deadline import Deadline  # noqa: F401
from app.models.project_node import ProjectNode  # noqa: F401
from app.models.system import System  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.requirement import Requirement  # noqa: F401
from app.models.requirement_relationship import RequirementRelationship  # noqa: F401
from app.models.risk import Risk  # noqa: F401
from app.models.validation_activity import ValidationActivity  # noqa: F401
from app.models.protocol import Protocol  # noqa: F401
from app.models.test_step import TestStep  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
from app.models.deviation import Deviation  # noqa: F401
from app.models.capa import CAPA  # noqa: F401
from app.models.traceability import Traceability  # noqa: F401
from app.models.approval import Approval  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.notification import Notification  # noqa: F401

__all__ = [
    "User",
    "Role",
    "Permission",
    "Client",
    "Project",
    "ProjectPhase",
    "Milestone",
    "Deadline",
    "ProjectNode",
    "System",
    "Document",
    "Requirement",
    "RequirementRelationship",
    "Risk",
    "ValidationActivity",
    "Protocol",
    "TestStep",
    "Evidence",
    "Attachment",
    "Deviation",
    "CAPA",
    "Traceability",
    "Approval",
    "AuditLog",
    "Report",
    "Notification",
]
