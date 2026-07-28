from app.integrations.base import AuthProviderAdapter


class AzureADAdapter(AuthProviderAdapter):
    """Stub adapter for AzureAD. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement AzureADAdapter.test_connection against the vendor API")

    def authenticate(self, token: str) -> dict:
        raise NotImplementedError("TODO: implement AzureADAdapter.authenticate against the vendor API")

