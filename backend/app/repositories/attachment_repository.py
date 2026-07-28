from sqlalchemy import select

from app.models.attachment import Attachment
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[Attachment]):
    model = Attachment

    def list_for_entity(self, entity_type: str, entity_id: str) -> list[Attachment]:
        stmt = select(self.model).where(
            self.model.entity_type == entity_type, self.model.entity_id == entity_id,
        )
        return list(self.db.execute(stmt).scalars().all())
