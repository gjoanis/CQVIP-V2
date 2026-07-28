from sqlalchemy.orm import Session

from app.models.client import Client
from app.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, db: Session):
        self.repo = ClientRepository(db)

    def get(self, client_id: str) -> Client:
        return self.repo.get_or_404(client_id)

    def list_all(self, offset: int = 0, limit: int = 100) -> list[Client]:
        return self.repo.list_all(offset=offset, limit=limit)

    def create(self, **fields) -> Client:
        return self.repo.create(Client(**fields))

    def update(self, client_id: str, **fields) -> Client:
        return self.repo.update(self.get(client_id), **fields)

    def delete(self, client_id: str) -> None:
        self.repo.delete(self.get(client_id))
