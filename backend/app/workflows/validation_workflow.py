from sqlalchemy.orm import Session

from app.models.enums import ValidationStatus
from app.models.protocol import Protocol
from app.models.test_step import TestStep
from app.repositories.validation_repository import ValidationRepository


class ValidationWorkflowEngine:
    def __init__(self, db: Session):
        self.db = db
        self.activities = ValidationRepository(db)

    def start(self, activity_id: str) -> None:
        activity = self.activities.get_or_404(activity_id)
        self.activities.update(activity, status=ValidationStatus.IN_PROGRESS)

    def record_step_result(self, step: TestStep, actual_result: str, passed: bool) -> None:
        step.actual_result = actual_result
        step.status = ValidationStatus.PASSED if passed else ValidationStatus.FAILED
        self.db.commit()
        self._roll_up(step.protocol)

    def _roll_up(self, protocol: Protocol) -> None:
        steps = protocol.test_steps
        if not steps:
            return
        activity = self.activities.get_or_404(protocol.validation_activity_id)
        if any(s.status == ValidationStatus.FAILED for s in steps):
            self.activities.update(activity, status=ValidationStatus.FAILED)
        elif all(s.status == ValidationStatus.PASSED for s in steps):
            self.activities.update(activity, status=ValidationStatus.PASSED)
