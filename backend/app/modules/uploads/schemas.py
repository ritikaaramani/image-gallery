# app/modules/uploads/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class UploadBase(BaseModel):
    id: uuid.UUID
    filename: str
    url: str
    content_type: str
    uploaded_at: datetime
    
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: Optional[int] = None
    thumbnail_url: Optional[str] = None
    exif: Optional[dict] = None

class UploadOut(UploadBase):
    uploader_id: Optional[uuid.UUID]
    description: Optional[str]
    tags: Optional[List[str]]
    privacy: Optional[str]

    class Config:
        orm_mode = True
        json_encoders = {
            uuid.UUID: str
        }
