from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Classify the following requirement into one category (Functional, Performance, Regulatory, Safety, Data Integrity, Interface, or Usability) and reply with just the category name.'
)


class RequirementClassification(AICapability):
    """Classifies a requirement into a standard category."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
