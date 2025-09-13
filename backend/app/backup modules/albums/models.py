from sqlalchemy import Column, String, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.modules.rights.models import Rights 
import uuid

from app.db.database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add the foreign key to link to the users table
    owner_id = Column(String(length=36), ForeignKey("users.id"))

    # Add the relationship to the User model, linking back to the 'albums' relationship
    owner = relationship("User", back_populates="albums")

    # Relationships
    images = relationship("Image", back_populates="album")
    rights = relationship("Rights", back_populates="album")
    
