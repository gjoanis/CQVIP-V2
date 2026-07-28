from app.integrations.base import ManufacturingSystemAdapter


class EmersonSyncadeAdapter(ManufacturingSystemAdapter):
    """Stub adapter for EmersonSyncade. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement EmersonSyncadeAdapter.test_connection against the vendor API")

    def read_tag(self, tag_name: str):
        raise NotImplementedError("TODO: implement EmersonSyncadeAdapter.read_tag against the vendor API")

    def write_tag(self, tag_name: str, value) -> None:
        raise NotImplementedError("TODO: implement EmersonSyncadeAdapter.write_tag against the vendor API")

