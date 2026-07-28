from app.integrations.base import ERPAdapter


class SAPAdapter(ERPAdapter):
    """Stub adapter for SAP. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement SAPAdapter.test_connection against the vendor API")

    def get_purchase_order(self, po_number: str) -> dict:
        raise NotImplementedError("TODO: implement SAPAdapter.get_purchase_order against the vendor API")

    def get_asset_record(self, asset_id: str) -> dict:
        raise NotImplementedError("TODO: implement SAPAdapter.get_asset_record against the vendor API")

