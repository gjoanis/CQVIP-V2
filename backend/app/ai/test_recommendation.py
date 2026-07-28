from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    'Suggest concrete test cases (steps and expected results) for the following requirement.'
)


class TestRecommendation(AICapability):
    """Suggests concrete test cases for a requirement."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
