# models.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys to link to a parent object
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id"), nullable=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Corrected relationships
    image = relationship("Image", back_populates="comments")
    user = relationship("User", back_populates="comments") # Corrected
