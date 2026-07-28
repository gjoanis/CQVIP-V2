from app.integrations.base import ValidationPlatformAdapter


class VeevaValidationAdapter(ValidationPlatformAdapter):
    """Stub adapter for VeevaValidation. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement VeevaValidationAdapter.test_connection against the vendor API")

    def push_protocol(self, protocol: dict) -> str:
        raise NotImplementedError("TODO: implement VeevaValidationAdapter.push_protocol against the vendor API")

    def fetch_execution_status(self, protocol_id: str) -> dict:
        raise NotImplementedError("TODO: implement VeevaValidationAdapter.fetch_execution_status against the vendor API")

