# app/modules/users/models.py
import uuid
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.modules.image_likes.models import ImageLike as Like

def generate_uuid_str():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(length=36), primary_key=True, default=generate_uuid_str, index=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    avatar_image_id = Column(String(length=36), nullable=True, index=True)

    # Relationships to images, likes, and albums
    images = relationship("Image", back_populates="author", cascade="all, delete-orphan")
    albums = relationship("Album", back_populates="owner", cascade="all, delete-orphan")
    likes = relationship("ImageLike", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
