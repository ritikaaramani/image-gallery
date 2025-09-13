import os
import uuid
import json
from app.db.database import get_db
from app.modules.uploads import models
from sqlalchemy.orm import Session

UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def migrate_old_uploads(db: Session):
    """
    Scan the uploads folder for non-UUID files and add them to the database
    so URLs work consistently.
    """
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        # skip directories and already UUID-named files
        if not os.path.isfile(file_path):
            continue
        name, ext = os.path.splitext(filename)
        try:
            # Try parsing name as UUID
            uuid.UUID(name)
            continue  # already UUID, skip
        except Exception:
            pass  # not UUID, proceed

        # Generate new UUID for this file
        new_id = str(uuid.uuid4())
        new_filename = f"{new_id}{ext}"
        new_path = os.path.join(UPLOAD_DIR, new_filename)

        # Rename the file on disk
        os.rename(file_path, new_path)

        # Add to database
        db_upload = models.Upload(
            id=new_id,
            filename=new_filename,
            storage_path=new_path,
            url=f"{BASE_URL}/uploads/{new_filename}",
            thumbnail_url=None,  # optionally generate thumbnail here
            content_type="image/jpeg",  # or detect dynamically
            width=None,
            height=None,
            size_bytes=os.path.getsize(new_path),
            uploader_id=None,
            description=None,
            tags=json.dumps([]),
            exif=json.dumps({}),
            privacy="public",
        )
        db.add(db_upload)
    db.commit()
    print("Old uploads migrated successfully!")

# Usage:
# from app.db.database import SessionLocal
# db = SessionLocal()
# migrate_old_uploads(db)
# db.close()
