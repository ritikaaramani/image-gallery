# app/modules/image_views/router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.database import get_db
from app.modules.image_views import schemas, service
from app.modules.images import models as image_models # Import the Image model
from app.auth.dependencies import get_current_user
from app.modules.users.schemas import User as UserSchema

router = APIRouter(prefix="/image_views", tags=["Image Views"])

@router.post("/", response_model=schemas.ImageView)
def create_view(
    view: schemas.ImageViewCreate, 
    user: UserSchema = Depends(get_current_user), # Get the current user
    db: Session = Depends(get_db)
):
    # Check if the image exists before creating a view
    image = db.query(image_models.Image).filter(image_models.Image.id == view.image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    # Pass image_id and user_id to the service
    return service.create_image_view(db=db, image_id=view.image_id, user_id=user.id)

@router.get("/", response_model=List[schemas.ImageView])
def read_views(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_image_views(db, skip=skip, limit=limit)

@router.get("/{view_id}", response_model=schemas.ImageView)
def read_view(view_id: uuid.UUID, db: Session = Depends(get_db)):
    db_view = service.get_image_view(db, view_id=view_id)
    if db_view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image view not found")
    return db_view

@router.delete("/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_view(view_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = service.delete_image_view(db, view_id=view_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image view not found")
    return

@router.delete("/admin/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_view(
    view_id: uuid.UUID,
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    deleted = service.delete_image_view(db, view_id=view_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image view not found")
    return
