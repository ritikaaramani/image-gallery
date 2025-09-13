# app/modules/sitemap/models.py
"""
Sitemap models adapted for an image/media platform.

IMPORTANT:
- These models are lightweight, DB-agnostic representations intended
  for use by the sitemap generator. If your project already has
  canonical Image/Album models inside `uploads`, `images`, or `gallery`
  modules, prefer using those and keep this file as a fallback or
  remove duplicates to avoid conflicts.
- IDs are stored as 36-char string UUIDs for portability across
  SQLite/Postgres without depending on the postgres UUID type.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Integer,
    Text,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.database import Base

# Helper to generate string UUIDs (works across DB backends)
def gen_uuid_str() -> str:
    return str(uuid.uuid4())


#
# Image model - represents a single image asset that can be included in the sitemap.
#
class Image(Base):
    __tablename__ = "images"

    # store UUID as string to be compatible with SQLite and Postgres
    id = Column(String(36), primary_key=True, default=gen_uuid_str, index=True)
    filename = Column(String, nullable=False)               # original filename
    title = Column(String, nullable=True)                   # optional title/caption
    description = Column(Text, nullable=True)
    slug = Column(String, nullable=True, unique=False)      # optional human slug for SEO
    storage_path = Column(String, nullable=False)           # internal path or object key
    url = Column(String, nullable=False)                    # public URL or page URL
    thumbnail_url = Column(String, nullable=True)           # thumbnail/preview URL
    content_type = Column(String, nullable=True)            # image/jpeg, image/png, etc.
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    exif = Column(Text, nullable=True)                      # JSON string of EXIF metadata
    tags = Column(Text, nullable=True)                      # JSON string array of tags
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    privacy = Column(String, default="public")              # public | unlisted | private

    # optional linkage to album
    album_id = Column(String(36), ForeignKey("albums.id"), nullable=True, index=True)
    album = relationship("Album", back_populates="images", passive_deletes=True)

    def url_for(self, base_url: str) -> str:
        """
        Build a public URL for the image page. Prefer a slug if present, otherwise use id.
        This method is used by sitemap generator to create loc entries.
        """
        base = base_url.rstrip("/")
        if self.slug:
            return f"{base}/images/{self.slug}"
        return f"{base}/images/{self.id}"

    def lastmod(self):
        """Return a datetime to use as lastmod in sitemaps (updated_at or uploaded_at)."""
        return self.updated_at or self.uploaded_at


#
# Album model - groups images and can be listed in sitemap
#
class Album(Base):
    __tablename__ = "albums"

    id = Column(String(36), primary_key=True, default=gen_uuid_str, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String, nullable=True, unique=False)
    cover_image_id = Column(String(36), nullable=True, index=True)  # reference to representative image id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    public = Column(Boolean, default=True)        # whether the album should be visible in public sitemap

    # relationship back to images
    images = relationship("Image", back_populates="album", cascade="all, delete-orphan", passive_deletes=True)

    def url_for(self, base_url: str) -> str:
        base = base_url.rstrip("/")
        if self.slug:
            return f"{base}/albums/{self.slug}"
        return f"{base}/albums/{self.id}"

    def lastmod(self):
        """Prefer updated_at, or fallback to created_at."""
        return self.updated_at or self.created_at


#
# Backwards-compatible Post and Page (kept with string-UUIDs)
# If your system still has Posts/Pages, the sitemap generator can include them.
#
class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=gen_uuid_str, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String, default="public")   # public / draft
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def url_for(self, base_url: str) -> str:
        return f"{base_url.rstrip('/')}/posts/{self.id}"

    def lastmod(self):
        return self.updated_at or self.created_at


class Page(Base):
    __tablename__ = "pages"

    id = Column(String(36), primary_key=True, default=gen_uuid_str, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    public = Column(Boolean, default=True)
    show_in_list = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def url_for(self, base_url: str) -> str:
        return f"{base_url.rstrip('/')}/pages/{self.id}"

    def lastmod(self):
        return self.updated_at or self.created_at
