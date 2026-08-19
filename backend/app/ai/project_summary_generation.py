from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    "You write the narrative section of a project status report for a "
    "quality leadership and inspection audience. Write three short sections using "
    "markdown '## ' headers -- Executive Summary, Risk & Gap Assessment, Recommendations "
    "-- each 1-3 sentences of plain prose, direct and factual, referencing the specific "
    "numbers given. No bullet points inside the sections, no commentary outside them."
)


class ProjectSummaryGeneration(AICapability):
    """Drafts the narrative portion of a project's Project Life Cycle Report from
    its live readiness metrics and gap analysis."""

    def run(
        self, *, project_name: str, lifecycle_readiness_pct: float,
        inspection_readiness_index_pct: float, execution_readiness_pct: float,
        current_stage: str, project_health: str, total_requirements: int,
        critical_or_high_open: int, awaiting_verification: int, open_risks: int,
        open_gap_count: int, top_gap_categories: list[str],
    ) -> str:
        prompt = (
            f"Project: {project_name}\n"
            f"Current lifecycle stage: {current_stage}\n"
            f"Project health: {project_health}\n"
            f"Overall Lifecycle Readiness: {lifecycle_readiness_pct}%\n"
            f"Inspection Readiness Index: {inspection_readiness_index_pct}%\n"
            f"Validation Execution Readiness: {execution_readiness_pct}%\n"
            f"Total requirements: {total_requirements}\n"
            f"Critical/high priority requirements still open: {critical_or_high_open}\n"
            f"Requirements awaiting verification: {awaiting_verification}\n"
            f"Open risks: {open_risks}\n"
            f"Open gaps identified: {open_gap_count}\n"
            f"Top gap categories: {', '.join(top_gap_categories) if top_gap_categories else 'none'}\n"
        )
        return complete(SYSTEM_PROMPT, prompt, max_tokens=800)
