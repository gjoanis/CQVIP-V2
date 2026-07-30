"""Generates the Current Project Summary Report: a Markdown document combining
a real Claude-written narrative with the live readiness metrics and gap
analysis already computed for the project dashboard
(app.workflows.project_readiness), saved to storage/generated_reports/ and
recorded as a Report row. Deliberately not called a "Validation Summary
Report" -- that term is reserved for a report summarizing executed
validation activities (IQ/OQ/PQ results), which this isn't.
"""
import os
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.project_summary_generation import ProjectSummaryGeneration
from app.config import get_settings
from app.models.project import Project
from app.models.report import Report
from app.services.report_service import ReportService
from app.workflows.project_readiness import compute_gap_analysis, compute_project_dashboard

REPORT_TYPE_PROJECT_SUMMARY = "project_summary"


def _top_gap_categories(open_gap_rows: list[dict], limit: int = 5) -> list[str]:
    counts = Counter(row["category"] or "Uncategorized" for row in open_gap_rows)
    return [f"{category} ({count})" for category, count in counts.most_common(limit)]


def _gap_table(open_gap_rows: list[dict], limit: int = 100) -> list[str]:
    lines = [
        "| Requirement | Category | Priority | Gap | Risk | Recommendation |",
        "|---|---|---|---|---|---|",
    ]
    for row in open_gap_rows[:limit]:
        lines.append(
            f"| {row['req_code']} | {row['category'] or '—'} | {row['priority'].value} | "
            f"{row['gap']} | {row['risk']} | {row['recommendation']} |"
        )
    if len(open_gap_rows) > limit:
        lines.append("")
        lines.append(f"_... and {len(open_gap_rows) - limit} more open gaps not shown._")
    return lines


def generate_project_summary_report(
    db: Session, project: Project, *, generated_by_id: str | None = None,
) -> Report:
    metrics = compute_project_dashboard(db, project.id)
    gap_rows = compute_gap_analysis(db, project.id, metrics["current_stage"])
    open_gap_rows = [row for row in gap_rows if row["gap"] != "None"]

    narrative = ProjectSummaryGeneration().run(
        project_name=project.name,
        lifecycle_readiness_pct=metrics["lifecycle_readiness_pct"],
        inspection_readiness_index_pct=metrics["inspection_readiness_index_pct"],
        execution_readiness_pct=metrics["execution_readiness_pct"],
        current_stage=metrics["current_stage"],
        project_health=metrics["project_health"],
        total_requirements=metrics["total_requirements"],
        critical_or_high_open=metrics["critical_or_high_open"],
        awaiting_verification=metrics["awaiting_verification"],
        open_risks=metrics["open_risks"],
        open_gap_count=len(open_gap_rows),
        top_gap_categories=_top_gap_categories(open_gap_rows),
    )

    generated_at = datetime.now(timezone.utc)
    lines = [
        f"# Current Project Summary Report — {project.name}",
        "",
        f"**Generated:** {generated_at.strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Project code:** {project.code}  ",
        f"**Current lifecycle stage:** {metrics['current_stage']}  ",
        f"**Project health:** {metrics['project_health'].upper()}",
        "",
        narrative.strip(),
        "",
        "## Readiness Metrics",
        "",
        f"- Overall Lifecycle Readiness: {metrics['lifecycle_readiness_pct']}%",
        f"- Inspection Readiness Index (IRI): {metrics['inspection_readiness_index_pct']}%",
        f"- Validation Execution Readiness: {metrics['execution_readiness_pct']}%",
        "",
        "## Phase Breakdown",
        "",
    ]
    for phase in metrics["phase_readiness"]:
        lines.append(f"- Phase {phase['phase']} — {phase['label']}: {phase['pct']}%")

    lines += [
        "",
        "## Requirements Summary",
        "",
        f"- Total requirements: {metrics['total_requirements']}",
        f"- Critical/high priority still open: {metrics['critical_or_high_open']}",
        f"- Awaiting verification: {metrics['awaiting_verification']}",
        f"- Open risks: {metrics['open_risks']}",
        f"- Open gaps identified: {len(open_gap_rows)}",
        "",
        "## Gap Analysis",
        "",
        *_gap_table(open_gap_rows),
    ]

    content = "\n".join(lines)

    settings = get_settings()
    dest_dir = os.path.join(settings.storage_root, "generated_reports", project.id)
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"project-summary-{generated_at.strftime('%Y%m%d%H%M%S')}.md"
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, "w") as f:
        f.write(content)

    return ReportService(db).record_generated(
        project_id=project.id,
        generated_by_id=generated_by_id,
        report_type=REPORT_TYPE_PROJECT_SUMMARY,
        title=f"Current Project Summary Report — {project.name}",
        file_path=dest_path,
    )
