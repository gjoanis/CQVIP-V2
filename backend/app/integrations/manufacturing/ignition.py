from app.integrations.base import ManufacturingSystemAdapter


class IgnitionAdapter(ManufacturingSystemAdapter):
    """Stub adapter for Ignition. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement IgnitionAdapter.test_connection against the vendor API")

    def read_tag(self, tag_name: str):
        raise NotImplementedError("TODO: implement IgnitionAdapter.read_tag against the vendor API")

    def write_tag(self, tag_name: str, value) -> None:
        raise NotImplementedError("TODO: implement IgnitionAdapter.write_tag against the vendor API")

