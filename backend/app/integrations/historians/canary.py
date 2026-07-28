from app.integrations.base import HistorianAdapter


class CanaryAdapter(HistorianAdapter):
    """Stub adapter for Canary. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement CanaryAdapter.test_connection against the vendor API")

    def query_range(self, tag_name: str, start, end) -> list[dict]:
        raise NotImplementedError("TODO: implement CanaryAdapter.query_range against the vendor API")

