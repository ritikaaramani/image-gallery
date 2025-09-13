# app/modules/uploads/models.py
import json
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Upload(Base):
    __tablename__ = "uploads"

    # store UUID as string for maximum portability (sqlite/postgres)
    id = Column(String(length=36), primary_key=True, index=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)   # path on disk or object key
    url = Column(String, nullable=False)            # public URL path (signed or static)
    thumbnail_url = Column(String, nullable=True)   # generated thumbnail URL
    content_type = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploader_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # user id reference
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)   # stored as JSON array string
    exif = Column(Text, nullable=True)   # JSON string of exif metadata
    privacy = Column(String, default="public")  # public, unlisted, private

    # New relationship to the content object (Image)
    image = relationship("Image", back_populates="upload")
