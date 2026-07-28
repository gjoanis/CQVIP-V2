from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Recommend a verification strategy (test, inspection, analysis, or demonstration) for the following requirement, with a one-sentence rationale.'
)


class VerificationStrategy(AICapability):
    """Recommends how a requirement should be verified."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
