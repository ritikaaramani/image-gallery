# app/modules/images/models.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.sql import func
from app.modules.rights.models import Rights
from app.modules.comments.models import Comment
import enum
from sqlalchemy.dialects.postgresql import UUID


class PrivacyLevel(str, enum.Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
    privacy = Column(Enum(PrivacyLevel), default=PrivacyLevel.PUBLIC)
    license = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    description = Column(Text, nullable=True)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    
    # New foreign key and relationship to the uploads table
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), unique=True)
    upload = relationship("Upload", back_populates="image")

    # Relationships
    comments = relationship("Comment", back_populates="image", cascade="all, delete-orphan")
    author = relationship("User", back_populates="images")
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id"), nullable=True)
    album = relationship("Album", back_populates="images")
    likes = relationship("ImageLike", back_populates="image", cascade="all, delete-orphan")
    rights = relationship("Rights", back_populates="image")
    views = relationship("ImageView", back_populates="image")
