from app.integrations.base import CloudAIAdapter


class GoogleVertexAIAdapter(CloudAIAdapter):
    """Stub adapter for GoogleVertexAI. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement GoogleVertexAIAdapter.test_connection against the vendor API")

    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        raise NotImplementedError("TODO: implement GoogleVertexAIAdapter.complete against the vendor API")

