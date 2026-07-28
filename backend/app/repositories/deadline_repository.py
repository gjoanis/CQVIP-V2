from app.models.deadline import Deadline
from app.repositories.base import BaseRepository


class DeadlineRepository(BaseRepository[Deadline]):
    model = Deadline
