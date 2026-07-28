import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PhaseStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class SystemType(str, enum.Enum):
    EQUIPMENT = "equipment"
    FACILITY_SYSTEM = "facility_system"
    UTILITY_SYSTEM = "utility_system"
    COMPUTERIZED_SYSTEM = "computerized_system"
    PROCESS = "process"
    OTHER = "other"


class RequirementStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    CLOSED = "closed"
    NOT_APPLICABLE = "not_applicable"


class RequirementDisposition(str, enum.Enum):
    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"


class RequirementPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class ValidationActivityType(str, enum.Enum):
    ENGINEERING_STUDY = "engineering_study"
    FAT = "fat"
    SAT = "sat"
    COMMISSIONING = "commissioning"
    IQ = "iq"
    OQ = "oq"
    PQ = "pq"
    FINAL_REPORT = "final_report"
    OTHER = "other"


class ValidationStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class DeviationSeverity(str, enum.Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class CAPAStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    CLOSED = "closed"


class NotificationType(str, enum.Enum):
    INFO = "info"
    DEADLINE = "deadline"
    APPROVAL_REQUEST = "approval_request"
    RISK_ALERT = "risk_alert"
    SYSTEM = "system"
