# app/modules/image_views/service.py
from sqlalchemy.orm import Session
from app.modules.image_views import models, schemas
from uuid import UUID
from typing import Optional, List

def create_image_view(db: Session, image_id: UUID, user_id: UUID) -> models.ImageView:
    """
    Creates a new image view record for the current user.
    """
    db_view = models.ImageView(image_id=image_id, user_id=user_id)
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view

def get_image_views(db: Session, skip: int = 0, limit: int = 100) -> list[models.ImageView]:
    """
    Retrieves a list of all image views.
    """
    return db.query(models.ImageView).offset(skip).limit(limit).all()

def get_image_view(db: Session, view_id: UUID) -> Optional[models.ImageView]:
    """
    Retrieves a single image view by its ID.
    """
    return db.query(models.ImageView).filter(models.ImageView.id == view_id).first()

def delete_image_view(db: Session, view_id: UUID) -> bool:
    """
    Deletes an image view by its ID.
    """
    view = db.query(models.ImageView).filter(models.ImageView.id == view_id).first()
    if view:
        db.delete(view)
        db.commit()
        return True
    return False
