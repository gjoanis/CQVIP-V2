from app.integrations.base import AuthProviderAdapter


class Auth0Adapter(AuthProviderAdapter):
    """Stub adapter for Auth0. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement Auth0Adapter.test_connection against the vendor API")

    def authenticate(self, token: str) -> dict:
        raise NotImplementedError("TODO: implement Auth0Adapter.authenticate against the vendor API")

