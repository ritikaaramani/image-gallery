# model.py
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.database import Base

class ImageLike(Base):
    __tablename__ = "likes" # Changed for consistency
    __table_args__ = {'extend_existing': True} 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    image = relationship("Image", back_populates="likes") # Changed to string literal
    user = relationship("User", back_populates="likes")
