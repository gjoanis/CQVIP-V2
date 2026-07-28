from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.project_node import ProjectNode
from app.repositories.base import BaseRepository

router = APIRouter(prefix="/projects/{project_id}/workspace", tags=["project-workspace"])


class NodeRepository(BaseRepository[ProjectNode]):
    model = ProjectNode


class NodeIn(BaseModel):
    parent_id: str | None = None
    node_type: str
    name: str
    order: int = 0


class NodeOut(NodeIn):
    id: str
    project_id: str

    model_config = {"from_attributes": True}


@router.get("/nodes", response_model=list[NodeOut])
def list_nodes(project_id: str, db: Session = Depends(get_db)):
    return [n for n in NodeRepository(db).list_all(limit=5000) if n.project_id == project_id]


@router.post("/nodes", response_model=NodeOut)
def create_node(project_id: str, payload: NodeIn, db: Session = Depends(get_db)):
    return NodeRepository(db).create(ProjectNode(project_id=project_id, **payload.model_dump()))
