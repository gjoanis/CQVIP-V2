from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


class UserIn(BaseModel):
    email: str
    full_name: str
    password: str
    role_id: str | None = None


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return UserService(db).list_all()


@router.post("", response_model=UserOut)
def create_user(payload: UserIn, db: Session = Depends(get_db)):
    return UserService(db).create(**payload.model_dump())


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    return UserService(db).get(user_id)
