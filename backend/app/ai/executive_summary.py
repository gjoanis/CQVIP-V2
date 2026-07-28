from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    "You write a short executive summary (3-5 sentences, one paragraph) of a "
    "pharma/GxP validation project's readiness status, for a quality leader "
    "audience. Be direct and factual, referencing the specific numbers given. "
    "No headers, no bullet points, no markdown -- plain prose only."
)


class ExecutiveSummary(AICapability):
    def run(self, *, lifecycle_readiness_pct: float, inspection_readiness_index_pct: float,
            current_stage: str, project_health: str, total_requirements: int,
            critical_or_high_open: int, awaiting_verification: int, open_risks: int) -> str:
        prompt = (
            f"Overall Lifecycle Readiness: {lifecycle_readiness_pct}%\n"
            f"Current lifecycle stage: {current_stage}\n"
            f"Inspection Readiness Index: {inspection_readiness_index_pct}%\n"
            f"Project Health: {project_health}\n"
            f"Total requirements: {total_requirements}\n"
            f"Critical/High priority requirements still unverified: {critical_or_high_open}\n"
            f"Requirements awaiting verification overall: {awaiting_verification}\n"
            f"Open risks: {open_risks}\n"
        )
        return complete(SYSTEM_PROMPT, prompt, max_tokens=400)
