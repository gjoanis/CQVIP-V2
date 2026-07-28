from app.models.validation_activity import ValidationActivity
from app.repositories.base import BaseRepository


class ValidationRepository(BaseRepository[ValidationActivity]):
    model = ValidationActivity
