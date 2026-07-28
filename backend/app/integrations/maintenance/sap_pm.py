from app.integrations.base import MaintenanceAdapter


class SAPPMAdapter(MaintenanceAdapter):
    """Stub adapter for SAPPM. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement SAPPMAdapter.test_connection against the vendor API")

    def list_assets(self, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError("TODO: implement SAPPMAdapter.list_assets against the vendor API")

    def get_asset(self, asset_id: str) -> dict:
        raise NotImplementedError("TODO: implement SAPPMAdapter.get_asset against the vendor API")

