from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from . import service, schemas
from uuid import UUID

router = APIRouter(prefix="/pages", tags=["pages"])

@router.post("/", response_model=schemas.Page, status_code=status.HTTP_201_CREATED)
def create_page(page: schemas.PageCreate, db: Session = Depends(get_db)):
    """
    Creates a new page.
    """
    return service.create_page(db=db, page=page)

@router.get("/", response_model=List[schemas.Page])
def read_pages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of all pages.
    """
    return service.get_pages(db, skip=skip, limit=limit)

@router.get("/{slug}", response_model=schemas.Page)
def read_page(slug: str, db: Session = Depends(get_db)):
    """
    Retrieves a single page by its slug.
    """
    db_page = service.get_page_by_slug(db, slug=slug)
    if db_page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return db_page

@router.put("/{page_id}", response_model=schemas.Page)
def update_page(page_id: UUID, page_update: schemas.PageCreate, db: Session = Depends(get_db)):
    """
    Updates an existing page by its ID.
    """
    db_page = service.update_page(db, page_id=page_id, page_update=page_update)
    if db_page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return db_page

@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(page_id: UUID, db: Session = Depends(get_db)):
    """
    Deletes a page by its ID.
    """
    success = service.delete_page(db, page_id=page_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return
