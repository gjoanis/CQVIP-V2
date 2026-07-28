from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientIn(BaseModel):
    name: str
    industry: str = ""
    contact_name: str = ""
    contact_email: str = ""
    address: str = ""
    notes: str = ""


class ClientOut(ClientIn):
    id: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return ClientService(db).list_all()


@router.post("", response_model=ClientOut)
def create_client(payload: ClientIn, db: Session = Depends(get_db)):
    return ClientService(db).create(**payload.model_dump())


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: str, db: Session = Depends(get_db)):
    return ClientService(db).get(client_id)


@router.put("/{client_id}", response_model=ClientOut)
def update_client(client_id: str, payload: ClientIn, db: Session = Depends(get_db)):
    return ClientService(db).update(client_id, **payload.model_dump())


@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: str, db: Session = Depends(get_db)):
    ClientService(db).delete(client_id)
