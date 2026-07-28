from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, email: str, full_name: str, password: str) -> User:
        if self.users.get_by_email(email):
            raise ValidationError(f"A user with email {email} already exists")
        user = User(email=email, full_name=full_name, hashed_password=hash_password(password))
        return self.users.create(user)

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.users.get_by_email(email)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    def login(self, email: str, password: str) -> str:
        user = self.authenticate(email, password)
        if not user:
            raise ValidationError("Invalid credentials")
        return create_access_token(subject=user.id)
