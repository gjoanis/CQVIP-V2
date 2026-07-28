from app.integrations.base import CloudAIAdapter


class OpenAIAdapter(CloudAIAdapter):
    """Stub adapter for OpenAI. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement OpenAIAdapter.test_connection against the vendor API")

    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        raise NotImplementedError("TODO: implement OpenAIAdapter.complete against the vendor API")

