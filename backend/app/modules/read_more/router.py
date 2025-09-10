from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.read_more import schemas, service

router = APIRouter()


@router.get("/settings", response_model=schemas.ReadMoreSettings)
def get_read_more_settings(db: Session = Depends(get_db)):
    settings = service.get_settings(db)
    if not settings:
        raise HTTPException(status_code=404, detail="ReadMore settings not found")
    return settings


@router.put("/settings", response_model=schemas.ReadMoreSettings)
def update_read_more_settings(
    data: schemas.ReadMoreSettingsCreate, 
    db: Session = Depends(get_db)
):
    updated = service.update_settings(db, data)
    return updated


@router.post("/markup")
def markup_post(
    text: str, 
    url: str = "#", 
    db: Session = Depends(get_db)
):
    result = service.markup_post_text(db, text, url)
    return {"markup": result}
