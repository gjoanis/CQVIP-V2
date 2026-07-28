from app.integrations.base import DocumentManagementAdapter


class OpenTextAdapter(DocumentManagementAdapter):
    """Stub adapter for OpenText. Implement against the vendor's SDK/REST API."""

    def __init__(self, config: dict):
        super().__init__(config)

    def test_connection(self) -> bool:
        raise NotImplementedError("TODO: implement OpenTextAdapter.test_connection against the vendor API")

    def list_documents(self, folder_id: str) -> list[dict]:
        raise NotImplementedError("TODO: implement OpenTextAdapter.list_documents against the vendor API")

    def upload_document(self, folder_id: str, file_path: str, name: str) -> str:
        raise NotImplementedError("TODO: implement OpenTextAdapter.upload_document against the vendor API")

    def download_document(self, document_id: str, dest_path: str) -> str:
        raise NotImplementedError("TODO: implement OpenTextAdapter.download_document against the vendor API")

