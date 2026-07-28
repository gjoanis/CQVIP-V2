from app.models.risk import Risk
from app.repositories.base import BaseRepository


class RiskRepository(BaseRepository[Risk]):
    model = Risk
