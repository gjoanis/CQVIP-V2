from app.models.fmea import FmeaAnalysis, FmeaLineItem
from app.repositories.base import BaseRepository


class FmeaAnalysisRepository(BaseRepository[FmeaAnalysis]):
    model = FmeaAnalysis


class FmeaLineItemRepository(BaseRepository[FmeaLineItem]):
    model = FmeaLineItem
