import json
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.modules.uploads import schemas
from app.modules.images.schemas import ImageResponse  # Import Image schema for response
from app.modules.users.schemas import User as UserSchema
from app.auth.dependencies import get_current_user
from app.modules.uploads.service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


def deserialize_upload(upload):
    """Ensure tags/exif are parsed and URL is corrected"""
    if upload:
        # Parse tags
        try:
            upload.tags = json.loads(upload.tags) if upload.tags else []
        except Exception:
            upload.tags = []
        # Parse exif
        try:
            upload.exif = json.loads(upload.exif) if upload.exif else {}
        except Exception:
            upload.exif = {}

        # ✅ Fix URL so frontend always gets /static/uploads/{filename}
        if hasattr(upload, "url") and upload.url:
            filename = os.path.basename(upload.url)
            upload.url = f"http://localhost:8000/static/uploads/{filename}"

    return upload


@router.get("/", response_model=List[schemas.UploadOut])
def list_uploads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    upload_service = UploadService()
    items = upload_service.list_uploads(db, skip=skip, limit=limit)
    return [deserialize_upload(item) for item in items]


@router.get("/{upload_id}", response_model=schemas.UploadOut)
def get_upload(upload_id: str, db: Session = Depends(get_db)):
    upload_service = UploadService()
    upload = upload_service.get_upload(db, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return deserialize_upload(upload)


@router.post("/", response_model=schemas.UploadOut, status_code=status.HTTP_201_CREATED)
async def create_upload(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string or comma-separated
    privacy: Optional[str] = Form("public"),
    db: Session = Depends(get_db),
    user: UserSchema = Depends(get_current_user),
):
    """Upload a new file and return its metadata"""
    parsed_tags = []
    if tags:
        try:
            parsed_tags = json.loads(tags)
            if not isinstance(parsed_tags, list):
                parsed_tags = []
        except Exception:
            # fallback to comma-separated
            parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]

    upload_service = UploadService()
    try:
        new_upload = upload_service.create_upload_from_file(
            db=db,
            file_obj=file,
            uploader_id=user.id,
            description=description,
            tags=parsed_tags,
            privacy=privacy,
        )
        return deserialize_upload(new_upload)
    except Exception as e:
        print(f"Upload service error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/{upload_id}", response_model=schemas.UploadOut)
def delete_upload(
    upload_id: str,
    db: Session = Depends(get_db),
    user: UserSchema = Depends(get_current_user),
):
    upload_service = UploadService()
    upload = upload_service.delete_upload(db, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return deserialize_upload(upload)
