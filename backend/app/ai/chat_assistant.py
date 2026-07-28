from app.ai.base import AICapability
from app.config import get_settings
from app.integrations.cloud_ai.anthropic_client import get_anthropic_client

SYSTEM_PROMPT = (
    "You are the CQVIP assistant, helping validation engineers navigate projects, "
    "requirements, risk, and compliance documentation. Be precise and cite project "
    "data you were given rather than guessing."
)


class ChatAssistant(AICapability):
    def run(self, message: str, history: list[dict] | None = None) -> str:
        settings = get_settings()
        client = get_anthropic_client()
        messages = (history or []) + [{"role": "user", "content": message}]
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return "".join(block.text for block in response.content if block.type == "text")
