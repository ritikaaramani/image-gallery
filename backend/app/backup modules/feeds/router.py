# router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from . import service

router = APIRouter(prefix="/feeds", tags=["feeds"])

@router.get("/images/rss")
def rss_images_feed(db: Session = Depends(get_db)):
    return service.generate_rss(db)

@router.get("/images/atom")
def atom_images_feed(db: Session = Depends(get_db)):
    return service.generate_atom(db)

@router.get("/albums/rss")
def rss_albums_feed(db: Session = Depends(get_db)):
    return service.generate_rss(db, content_type="albums")

@router.get("/albums/atom")
def atom_albums_feed(db: Session = Depends(get_db)):
    return service.generate_atom(db, content_type="albums")
