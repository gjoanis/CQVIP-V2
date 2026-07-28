from abc import ABC, abstractmethod


class IntegrationAdapter(ABC):
    """Base for every external-system adapter. Subclass per category below, then per vendor."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        raise NotImplementedError


class DocumentManagementAdapter(IntegrationAdapter):
    @abstractmethod
    def list_documents(self, folder_id: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def upload_document(self, folder_id: str, file_path: str, name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def download_document(self, document_id: str, dest_path: str) -> str:
        raise NotImplementedError


class ValidationPlatformAdapter(IntegrationAdapter):
    @abstractmethod
    def push_protocol(self, protocol: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def fetch_execution_status(self, protocol_id: str) -> dict:
        raise NotImplementedError


class QMSAdapter(IntegrationAdapter):
    @abstractmethod
    def create_deviation(self, deviation: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_capa(self, capa: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_record_status(self, record_id: str) -> dict:
        raise NotImplementedError


class MaintenanceAdapter(IntegrationAdapter):
    @abstractmethod
    def list_assets(self, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_asset(self, asset_id: str) -> dict:
        raise NotImplementedError


class ManufacturingSystemAdapter(IntegrationAdapter):
    @abstractmethod
    def read_tag(self, tag_name: str):
        raise NotImplementedError

    @abstractmethod
    def write_tag(self, tag_name: str, value) -> None:
        raise NotImplementedError


class LaboratorySystemAdapter(IntegrationAdapter):
    @abstractmethod
    def fetch_results(self, sample_id: str) -> dict:
        raise NotImplementedError


class HistorianAdapter(IntegrationAdapter):
    @abstractmethod
    def query_range(self, tag_name: str, start, end) -> list[dict]:
        raise NotImplementedError


class ERPAdapter(IntegrationAdapter):
    @abstractmethod
    def get_purchase_order(self, po_number: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_asset_record(self, asset_id: str) -> dict:
        raise NotImplementedError


class CloudAIAdapter(IntegrationAdapter):
    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        raise NotImplementedError


class AuthProviderAdapter(IntegrationAdapter):
    @abstractmethod
    def authenticate(self, token: str) -> dict:
        raise NotImplementedError
