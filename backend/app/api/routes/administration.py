from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.role import Role
from app.repositories.base import BaseRepository

router = APIRouter(prefix="/admin", tags=["administration"])


class RoleRepository(BaseRepository[Role]):
    model = Role


@router.get("/roles")
def list_roles(db: Session = Depends(get_db)):
    return RoleRepository(db).list_all()
