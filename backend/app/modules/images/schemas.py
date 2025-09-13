# app/modules/images/schemas.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ImageBase(BaseModel):
    title: str
    caption: Optional[str] = None
    privacy: str = "public"
    album_id: Optional[UUID] = None
    license: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class ImageResponse(BaseModel):
    id: UUID
    title: str
    caption: Optional[str]
    privacy: str
    license: Optional[str]
    album_id: Optional[UUID] = None
    filename: str
    mime_type: str

    class Config:
        orm_mode = True

