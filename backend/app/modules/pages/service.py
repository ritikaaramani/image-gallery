from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID
from typing import List, Optional

def get_page(db: Session, page_id: UUID) -> Optional[models.Page]:
    """
    Retrieves a page by its ID.
    """
    return db.query(models.Page).filter(models.Page.id == page_id).first()

def get_page_by_slug(db: Session, slug: str) -> Optional[models.Page]:
    """
    Retrieves a page by its unique slug.
    """
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def get_pages(db: Session, skip: int = 0, limit: int = 100) -> List[models.Page]:
    """
    Retrieves all pages with optional pagination.
    """
    return db.query(models.Page).offset(skip).limit(limit).all()

def create_page(db: Session, page: schemas.PageCreate) -> models.Page:
    """
    Creates a new page in the database.
    """
    db_page = models.Page(
        title=page.title,
        slug=page.slug,
        content=page.content,
        # Default values are handled by the model, but you can override here
        # public=page.public,
        # show_in_list=page.show_in_list,
    )
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, page_id: UUID, page_update: schemas.PageCreate) -> Optional[models.Page]:
    """
    Updates an existing page with new data.
    """
    db_page = get_page(db, page_id=page_id)
    if db_page:
        for key, value in page_update.model_dump().items():
            setattr(db_page, key, value)
        db.commit()
        db.refresh(db_page)
    return db_page

def delete_page(db: Session, page_id: UUID) -> bool:
    """
    Deletes a page by its ID.
    """
    db_page = get_page(db, page_id=page_id)
    if db_page:
        db.delete(db_page)
        db.commit()
        return True
    return False
