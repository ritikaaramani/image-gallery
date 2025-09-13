from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.modules.rights import schemas, service

router = APIRouter(prefix="/rights", tags=["Rights"])
rights_service = service.RightsService()


@router.post("/", response_model=schemas.RightsOut, status_code=status.HTTP_201_CREATED)
def create_rights(rights: schemas.RightsCreate, db: Session = Depends(get_db)):
    return rights_service.create_rights(db, rights)


@router.get("/{rights_id}", response_model=schemas.RightsOut)
def get_rights(rights_id: UUID, db: Session = Depends(get_db)):
    rights = rights_service.get_rights(db, rights_id)
    if not rights:
        raise HTTPException(status_code=404, detail="Rights not found")
    return rights


@router.put("/{rights_id}", response_model=schemas.RightsOut)
def update_rights(rights_id: UUID, update_data: schemas.RightsUpdate, db: Session = Depends(get_db)):
    return rights_service.update_rights(db, rights_id, update_data)


@router.delete("/{rights_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rights(rights_id: UUID, db: Session = Depends(get_db)):
    deleted = rights_service.delete_rights(db, rights_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rights not found")
    return
