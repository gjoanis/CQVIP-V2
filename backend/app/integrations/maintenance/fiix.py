from app.integrations.base import MaintenanceAdapter


class FiixAdapter(MaintenanceAdapter):
    """Stub adapter for Fiix. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement FiixAdapter.test_connection against the vendor API")

    def list_assets(self, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError("TODO: implement FiixAdapter.list_assets against the vendor API")

    def get_asset(self, asset_id: str) -> dict:
        raise NotImplementedError("TODO: implement FiixAdapter.get_asset against the vendor API")

