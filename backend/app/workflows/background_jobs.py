"""Minimal in-process job registry.

Swap this for Celery / RQ / APScheduler once you need retries, persistence,
or multi-process workers -- the call sites (job functions below) don't change.
"""
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.workflows.deadline_tracking import notify_upcoming_deadlines

JOB_REGISTRY: dict[str, Callable[[Session], object]] = {
    "notify_upcoming_deadlines": notify_upcoming_deadlines,
}


def run_job(name: str) -> object:
    job = JOB_REGISTRY[name]
    db = SessionLocal()
    try:
        return job(db)
    finally:
        db.close()
