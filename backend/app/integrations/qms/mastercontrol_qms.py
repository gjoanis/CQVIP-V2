from app.integrations.base import QMSAdapter


class MasterControlQMSAdapter(QMSAdapter):
    """Stub adapter for MasterControlQMS. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement MasterControlQMSAdapter.test_connection against the vendor API")

    def create_deviation(self, deviation: dict) -> str:
        raise NotImplementedError("TODO: implement MasterControlQMSAdapter.create_deviation against the vendor API")

    def create_capa(self, capa: dict) -> str:
        raise NotImplementedError("TODO: implement MasterControlQMSAdapter.create_capa against the vendor API")

    def get_record_status(self, record_id: str) -> dict:
        raise NotImplementedError("TODO: implement MasterControlQMSAdapter.get_record_status against the vendor API")

