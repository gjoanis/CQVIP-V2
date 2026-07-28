from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'You are a regulatory assistant. Answer questions about FDA, EMA, MHRA, ICH, and GAMP 5 and related standards, citing sources where possible.'
)


class RegulatoryAssistant(AICapability):
    """Answers questions grounded in the regulatory knowledge library."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
