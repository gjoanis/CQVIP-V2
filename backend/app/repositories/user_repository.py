from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str):
        stmt = select(self.model).where(self.model.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
