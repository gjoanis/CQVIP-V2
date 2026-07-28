from app.integrations.base import LaboratorySystemAdapter


class LabWareLIMSAdapter(LaboratorySystemAdapter):
    """Stub adapter for LabWareLIMS. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement LabWareLIMSAdapter.test_connection against the vendor API")

    def fetch_results(self, sample_id: str) -> dict:
        raise NotImplementedError("TODO: implement LabWareLIMSAdapter.fetch_results against the vendor API")

