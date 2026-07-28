from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'You are an engineering assistant for automation, process, and equipment questions in a GxP validation context.'
)


class EngineeringAssistant(AICapability):
    """Answers engineering questions about systems and equipment under validation."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
