from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Compare the following text against the referenced regulation or standard and list discrepancies, one per line.'
)


class RegulatoryComparison(AICapability):
    """Compares a document or requirement against a named regulation or standard."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
