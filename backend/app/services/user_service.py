from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get(self, user_id: str) -> User:
        return self.repo.get_or_404(user_id)

    def list_all(self, offset: int = 0, limit: int = 100) -> list[User]:
        return self.repo.list_all(offset=offset, limit=limit)

    def create(self, *, email: str, full_name: str, password: str, role_id: str | None = None) -> User:
        user = User(email=email, full_name=full_name, hashed_password=hash_password(password), role_id=role_id)
        return self.repo.create(user)

    def deactivate(self, user_id: str) -> User:
        return self.repo.update(self.get(user_id), is_active=False)
