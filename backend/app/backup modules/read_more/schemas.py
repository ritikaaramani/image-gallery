import uuid
from pydantic import BaseModel
from typing import Optional


class ReadMoreSettingsBase(BaseModel):
    apply_to_feeds: bool
    default_text: str


class ReadMoreSettingsCreate(ReadMoreSettingsBase):
    id: Optional[uuid.UUID] = None


class ReadMoreSettings(ReadMoreSettingsBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
