import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.database import Base


class Rights(Base):
    __tablename__ = "rights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link to albums or images
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=True)

    can_view = Column(Boolean, default=True)
    can_upload = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    
    # Content rights
    rights_title = Column(String, nullable=True)
    rights_holder = Column(String, nullable=True)
    rights_licence = Column(String, nullable=True)

    # User permissions
    read_users = Column(ARRAY(String), default=[])
    edit_users = Column(ARRAY(String), default=[])
    comment_users = Column(ARRAY(String), default=[])

    # Relationships
    album = relationship("Album", back_populates="rights")
    image = relationship("Image", back_populates="rights")
