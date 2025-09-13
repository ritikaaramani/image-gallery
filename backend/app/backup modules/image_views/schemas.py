# app/modules/image_views/schemas.py
from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class ImageViewBase(BaseModel):
    image_id: uuid.UUID
    # We no longer need user_id here as it's passed from the router
    
class ImageViewCreate(ImageViewBase):
    pass
    
class ImageView(ImageViewBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    viewed_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: str
        }
