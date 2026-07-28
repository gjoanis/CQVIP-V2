from app.integrations.base import CloudAIAdapter


class AzureOpenAIAdapter(CloudAIAdapter):
    """Stub adapter for AzureOpenAI. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement AzureOpenAIAdapter.test_connection against the vendor API")

    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        raise NotImplementedError("TODO: implement AzureOpenAIAdapter.complete against the vendor API")

