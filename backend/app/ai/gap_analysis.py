from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Given the following requirements and their current validation coverage, list any gaps, one per line.'
)


class GapAnalysis(AICapability):
    """Flags gaps between requirements and current validation coverage."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
