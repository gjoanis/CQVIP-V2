from app.ai.base import AICapability
from app.integrations.cloud_ai.anthropic_client import complete

SYSTEM_PROMPT = (
    "You are a project assistant. Answer questions about the given project's status, schedule, and risks using only the context provided."
)


class ProjectAssistant(AICapability):
    """Answers questions about a specific project's status, schedule, and risk."""

    def run(self, text: str, **kwargs) -> str:
        return complete(SYSTEM_PROMPT, text)
