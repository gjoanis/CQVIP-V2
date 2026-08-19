"""Derives cross-project trend and leaderboard data purely from timestamps
already recorded on Requirement, Risk, and Traceability rows (created_at /
updated_at) -- no periodic snapshot job needed, and it works retroactively on
data that already exists.

Caveat: updated_at reflects the most recent edit to a row, not a per-field
change history, so reconstructing "was this requirement verified as of date
X" is an approximation -- accurate for the common case of a field being set
once and left alone, but a requirement edited again *after* being verified
will appear to become verified only as of that later edit. Good enough for
directional trends; not a substitute for a true audit-trail replay.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RequirementStatus
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.risk import Risk
from app.models.traceability import Traceability


def _pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def _naive_utc(dt: datetime) -> datetime:
    """Postgres returns timezone-aware datetimes for these columns; SQLite
    (local dev) returns naive ones. Normalizing everything to naive UTC keeps
    comparisons working the same way in both environments."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _weekly_buckets(weeks: int) -> list[datetime]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return [now - timedelta(weeks=weeks - 1 - i) for i in range(weeks)]


def _earliest_protocol_link_dates(db: Session, project_id: str) -> dict[str, datetime]:
    rows = db.execute(
        select(Traceability.requirement_id, Traceability.created_at).where(
            Traceability.project_id == project_id, Traceability.protocol_id.is_not(None),
        )
    ).all()
    earliest: dict[str, datetime] = {}
    for requirement_id, created_at in rows:
        created_at = _naive_utc(created_at)
        if requirement_id not in earliest or created_at < earliest[requirement_id]:
            earliest[requirement_id] = created_at
    return earliest


def _trend_points(
    requirements: list[Requirement], risks: list[Risk],
    protocol_link_dates: dict[str, datetime], weeks: int,
) -> list[dict]:
    points = []
    for bucket_date in _weekly_buckets(weeks):
        as_of = [r for r in requirements if _naive_utc(r.created_at) <= bucket_date]
        total = len(as_of)

        def touched(r: Requirement) -> bool:
            return _naive_utc(r.updated_at) <= bucket_date

        phase1 = _pct(sum(1 for r in as_of if r.status != RequirementStatus.OPEN and touched(r)), total)
        phase2 = _pct(sum(1 for r in as_of if r.risk and touched(r)), total)
        phase3 = _pct(
            sum(1 for r in as_of if protocol_link_dates.get(r.id) and protocol_link_dates[r.id] <= bucket_date),
            total,
        )
        verified_now = sum(1 for r in as_of if r.verified and touched(r))
        phase4 = _pct(verified_now, total)
        phase5 = _pct(sum(1 for r in as_of if r.status == RequirementStatus.CLOSED and touched(r)), total)
        readiness = round((phase1 + phase2 + phase3 + phase4 + phase5) / 5, 1) if total else 0.0

        open_risks = sum(
            1 for r in risks
            if _naive_utc(r.created_at) <= bucket_date
            and not (r.status.value == "closed" and _naive_utc(r.updated_at) <= bucket_date)
        )

        points.append({
            "date": bucket_date.date().isoformat(),
            "requirements_total": total,
            "requirements_verified": verified_now,
            "lifecycle_readiness_pct": readiness,
            "open_risks": open_risks,
        })
    return points


def compute_portfolio_trends(db: Session, owner_id: str, weeks: int = 12) -> dict:
    projects = list(db.execute(select(Project).where(Project.owner_id == owner_id)).scalars())
    rows = []
    for project in projects:
        requirements = list(
            db.execute(select(Requirement).where(Requirement.project_id == project.id)).scalars()
        )
        risks = list(db.execute(select(Risk).where(Risk.project_id == project.id)).scalars())
        protocol_link_dates = _earliest_protocol_link_dates(db, project.id)
        rows.append({
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "points": _trend_points(requirements, risks, protocol_link_dates, weeks),
        })
    return {"weeks": weeks, "projects": rows}


def compute_leaderboard(db: Session, owner_id: str) -> dict:
    """Ranks projects by derived cycle-time and throughput so the fastest,
    most efficient projects surface first -- these are the ones worth mining
    for best practices to apply elsewhere."""
    projects = list(db.execute(select(Project).where(Project.owner_id == owner_id)).scalars())
    rows = []
    for project in projects:
        requirements = list(
            db.execute(select(Requirement).where(Requirement.project_id == project.id)).scalars()
        )
        risks = list(db.execute(select(Risk).where(Risk.project_id == project.id)).scalars())

        verified = [r for r in requirements if r.verified]
        req_days = [(r.updated_at - r.created_at).total_seconds() / 86400 for r in verified]
        closed_risks = [r for r in risks if r.status.value == "closed"]
        risk_days = [(r.updated_at - r.created_at).total_seconds() / 86400 for r in closed_risks]

        rows.append({
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "requirement_count": len(requirements),
            "requirement_verified_count": len(verified),
            "requirement_verification_rate_pct": _pct(len(verified), len(requirements)),
            "avg_requirement_verification_days": round(sum(req_days) / len(req_days), 1) if req_days else None,
            "risk_count": len(risks),
            "closed_risk_count": len(closed_risks),
            "avg_risk_closure_days": round(sum(risk_days) / len(risk_days), 1) if risk_days else None,
        })
    return {"projects": rows}
