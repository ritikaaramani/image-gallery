from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AlbumBase(BaseModel):
    title: str
    description: Optional[str] = None


class AlbumCreate(AlbumBase):
    pass


class AlbumUpdate(AlbumBase):
    pass


class Album(AlbumBase):
    id: UUID
    slug: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {UUID: lambda v: str(v)}
