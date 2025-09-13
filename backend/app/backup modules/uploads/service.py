# app/modules/uploads/service.py
import os
import uuid
import json
from sqlalchemy.orm import Session
from app.modules.uploads import models, schemas
from typing import Optional, List, Dict, Any
from PIL import Image, ExifTags
from io import BytesIO
import shutil
from fastapi import UploadFile, HTTPException, status
from app.modules.images import models as image_models # Import Image model

# Configuration via environment variables (fallbacks)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
THUMBNAIL_SIZE = (300, 300)  # px
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")  # used to build public URLs; override in prod

# ensure upload dir exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "thumbs"), exist_ok=True)

class UploadService:
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.thumb_dir = os.path.join(self.upload_dir, "thumbs")

    def _save_file_to_disk(self, upload_file, dest_path: str) -> None:
        """
        Save UploadFile-like object to dest_path atomically.
        """
        if hasattr(upload_file, "file"):
            fh = upload_file.file
            fh.seek(0)
            with open(dest_path, "wb") as out_f:
                shutil.copyfileobj(fh, out_f)
            fh.seek(0)
        else:
            with open(dest_path, "wb") as out_f:
                out_f.write(upload_file.read())

    def _extract_exif(self, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Extract EXIF from Pillow Image and return dictionary with human keys.
        """
        exif_data = {}
        try:
            raw_exif = pil_image._getexif()
            if not raw_exif:
                return {}
            for tag_id, value in raw_exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                try:
                    json.dumps(value)
                    exif_data[tag] = value
                except Exception:
                    exif_data[tag] = str(value)
        except Exception:
            return {}
        return exif_data

    def _make_thumbnail(self, pil_image: Image.Image, thumb_path: str) -> None:
        """
        Create a thumbnail and save to thumb_path.
        """
        try:
            im = pil_image.copy()
            im.thumbnail(THUMBNAIL_SIZE)
            im.save(thumb_path, format="JPEG", quality=85)
        except Exception as e:
            raise

    def create_upload_from_file(
        self,
        db: Session,
        file_obj: UploadFile,
        uploader_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        privacy: Optional[str] = "public",
    ) -> models.Upload:
        """
        Save file, extract metadata, generate thumbnail, and persist Upload records.
        """
        upload_id = str(uuid.uuid4())
        original_filename = getattr(file_obj, "filename", "upload")
        ext = os.path.splitext(original_filename)[1].lower() or ".jpg"
        safe_filename = f"{upload_id}{ext}"
        dest_path = os.path.join(self.upload_dir, safe_filename)

        try:
            self._save_file_to_disk(file_obj, dest_path)
            size_bytes = os.path.getsize(dest_path)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save file: {e}")

        width = height = None
        exif_data = {}
        thumbnail_url = None
        try:
            with Image.open(dest_path) as im:
                width, height = im.size
                exif_data = self._extract_exif(im)
                thumb_name = f"{upload_id}_thumb.jpg"
                thumb_path = os.path.join(self.thumb_dir, thumb_name)
                self._make_thumbnail(im, thumb_path)
                thumbnail_url = f"{BASE_URL}/uploads/thumbs/{thumb_name}"
        except Exception:
            pass

        public_url = f"{BASE_URL}/uploads/{safe_filename}"

        db_upload = models.Upload(
            id=upload_id,
            filename=original_filename,
            storage_path=dest_path,
            url=public_url,
            thumbnail_url=thumbnail_url,
            content_type=getattr(file_obj, "content_type", "application/octet-stream"),
            width=width,
            height=height,
            size_bytes=size_bytes,
            uploader_id=uploader_id,
            description=description,
            tags=json.dumps(tags or []),
            exif=json.dumps(exif_data or {}),
            privacy=privacy or "public",
        )
        db.add(db_upload)
        db.commit()
        db.refresh(db_upload)

        return db_upload


    # CRUD helpers
    def get_upload(self, db: Session, upload_id: str) -> Optional[models.Upload]:
        return db.query(models.Upload).filter(models.Upload.id == str(upload_id)).first()

    def list_uploads(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Upload).offset(skip).limit(limit).all()

    def delete_upload(self, db: Session, upload_id: str) -> Optional[models.Upload]:
        upload = self.get_upload(db, upload_id)
        if not upload:
            return None

        # also delete the associated image record if it exists
        if upload.image:
            db.delete(upload.image)
        
        try:
            if upload.storage_path and os.path.exists(upload.storage_path):
                os.remove(upload.storage_path)
            if upload.thumbnail_url:
                thumb_filename = os.path.basename(upload.thumbnail_url)
                thumb_path = os.path.join(self.thumb_dir, thumb_filename)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        except Exception:
            pass

        db.delete(upload)
        db.commit()
        return upload
