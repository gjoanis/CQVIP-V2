from app.models.traceability import Traceability
from app.repositories.base import BaseRepository


class TraceabilityRepository(BaseRepository[Traceability]):
    model = Traceability
