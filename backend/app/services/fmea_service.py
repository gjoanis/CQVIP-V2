from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.fmea import FmeaAnalysis, FmeaLineItem
from app.repositories.fmea_repository import FmeaAnalysisRepository, FmeaLineItemRepository


class FmeaService:
    def __init__(self, db: Session):
        self.db = db
        self.analyses = FmeaAnalysisRepository(db)
        self.items = FmeaLineItemRepository(db)

    def list_for_project(self, project_id: str) -> list[FmeaAnalysis]:
        stmt = select(FmeaAnalysis).where(FmeaAnalysis.project_id == project_id)
        return list(self.db.execute(stmt).scalars().all())

    def get(self, fmea_id: str) -> FmeaAnalysis:
        return self.analyses.get_or_404(fmea_id)

    def create(self, **fields) -> FmeaAnalysis:
        return self.analyses.create(FmeaAnalysis(**fields))

    def update(self, fmea_id: str, **fields) -> FmeaAnalysis:
        return self.analyses.update(self.get(fmea_id), **fields)

    def list_items(self, fmea_id: str) -> list[FmeaLineItem]:
        stmt = select(FmeaLineItem).where(FmeaLineItem.fmea_id == fmea_id).order_by(FmeaLineItem.order)
        return list(self.db.execute(stmt).scalars().all())

    def create_item(self, **fields) -> FmeaLineItem:
        # Column defaults (severity/occurrence/detection=1) only apply at DB
        # flush time, not on the freshly-constructed Python object -- set them
        # explicitly here so _rpn() below isn't multiplying against None.
        fields.setdefault("severity", 1)
        fields.setdefault("occurrence", 1)
        fields.setdefault("detection", 1)
        item = FmeaLineItem(**fields)
        item.rpn = self._rpn(item.severity, item.occurrence, item.detection)
        return self.items.create(item)

    def get_item_in_fmea(self, fmea_id: str, item_id: str) -> FmeaLineItem:
        """Fetches item_id but 404s unless it's actually a row of fmea_id --
        without this, .../{fmea_id}/items/{item_id} would silently accept an
        item_id from a *different* FMEA the URL's fmea_id has no relation to."""
        item = self.items.get_or_404(item_id)
        if item.fmea_id != fmea_id:
            raise NotFoundError("FmeaLineItem", item_id)
        return item

    def update_item(self, fmea_id: str, item_id: str, **fields) -> FmeaLineItem:
        item = self.items.update(self.get_item_in_fmea(fmea_id, item_id), **fields)
        updates = {"rpn": self._rpn(item.severity, item.occurrence, item.detection)}
        if item.resulting_severity and item.resulting_occurrence and item.resulting_detection:
            updates["resulting_rpn"] = self._rpn(
                item.resulting_severity, item.resulting_occurrence, item.resulting_detection,
            )
        return self.items.update(item, **updates)

    def delete_item(self, fmea_id: str, item_id: str) -> None:
        self.items.delete(self.get_item_in_fmea(fmea_id, item_id))

    def delete(self, fmea_id: str) -> None:
        for item in self.list_items(fmea_id):
            self.items.delete(item)
        self.analyses.delete(self.get(fmea_id))

    @staticmethod
    def _rpn(severity: int, occurrence: int, detection: int) -> int:
        return severity * occurrence * detection
