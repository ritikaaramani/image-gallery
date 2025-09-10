# schemas.py
import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str = Field(..., description="The content of the comment.")
    
class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class CommentSchema(CommentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] # updated_at should be optional for creation
    
    # New fields to replace post_id
    album_id: uuid.UUID | None = None
    image_id: uuid.UUID | None = None
    user_id: uuid.UUID
    
    class Config:
        orm_mode = True # Correct setting for SQLAlchemy integration
