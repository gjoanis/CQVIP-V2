from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Summarize the following requirements in a few sentences suitable for an executive audience.'
)


class RequirementSummarization(AICapability):
    """Summarizes a set of requirements for a non-technical audience."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
