import uuid
from pydantic import BaseModel
from typing import List, Optional


class RightsBase(BaseModel):
    rights_title: Optional[str] = None
    rights_holder: Optional[str] = None
    rights_licence: Optional[str] = None
    read_users: List[str] = []
    edit_users: List[str] = []
    comment_users: List[str] = []


class RightsCreate(RightsBase):
    album_id: Optional[uuid.UUID] = None
    image_id: Optional[uuid.UUID] = None


class RightsUpdate(RightsBase):
    pass


class RightsOut(RightsBase):
    id: uuid.UUID
    album_id: Optional[uuid.UUID] = None
    image_id: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True
        json_encoders = {uuid.UUID: str}
