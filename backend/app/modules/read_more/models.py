import uuid
from sqlalchemy import Column, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class ReadMoreSettings(Base):
    __tablename__ = "read_more_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apply_to_feeds = Column(Boolean, default=False, nullable=False)
    default_text = Column(Text, default="", nullable=False)
