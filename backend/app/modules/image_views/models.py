import uuid
from sqlalchemy import Column, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class ImageView(Base):
    __tablename__ = "image_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    extend_existing=True

    # Relationships
    image = relationship("Image", back_populates="views")
    user = relationship("User", viewonly=True, primaryjoin="ImageView.user_id==foreign(User.id)")
