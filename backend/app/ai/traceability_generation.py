from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Given the following requirements and test steps, propose traceability links between them.'
)


class TraceabilityGeneration(AICapability):
    """Proposes requirement-to-test traceability links."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
