# schemas.py
from pydantic import BaseModel
from uuid import UUID

class LikeBase(BaseModel):
    image_id: UUID
    user_id: UUID

class LikeCreate(LikeBase):
    pass
