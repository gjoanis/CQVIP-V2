from app.integrations.base import QMSAdapter


class TrackWiseAdapter(QMSAdapter):
    """Stub adapter for TrackWise. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement TrackWiseAdapter.test_connection against the vendor API")

    def create_deviation(self, deviation: dict) -> str:
        raise NotImplementedError("TODO: implement TrackWiseAdapter.create_deviation against the vendor API")

    def create_capa(self, capa: dict) -> str:
        raise NotImplementedError("TODO: implement TrackWiseAdapter.create_capa against the vendor API")

    def get_record_status(self, record_id: str) -> dict:
        raise NotImplementedError("TODO: implement TrackWiseAdapter.get_record_status against the vendor API")

