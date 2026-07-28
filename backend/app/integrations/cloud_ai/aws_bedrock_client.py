from app.integrations.base import CloudAIAdapter


class AWSBedrockAdapter(CloudAIAdapter):
    """Stub adapter for AWSBedrock. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement AWSBedrockAdapter.test_connection against the vendor API")

    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        raise NotImplementedError("TODO: implement AWSBedrockAdapter.complete against the vendor API")

