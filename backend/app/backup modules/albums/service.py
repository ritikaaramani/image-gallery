from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
import re
from typing import List, Optional

from app.modules.albums import models, schemas
from app.modules.rights import service as rights_service
from app.modules.users import schemas as user_schemas
from app.modules.rights.service import RightsService
from app.modules.images import models as image_models

rights_service = RightsService()

class AlbumService:
    def generate_slug(self, title: str) -> str:
        slug = title.strip().lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug

    def create_album(self, db: Session, album_data: schemas.AlbumCreate, author_id: str) -> models.Album:
        slug = self.generate_slug(album_data.title)

        existing = db.query(models.Album).filter(models.Album.slug == slug).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Album with this title already exists")

        album = models.Album(
            title=album_data.title,
            description=album_data.description,
            slug=slug,
            owner_id=author_id
        )
        db.add(album)
        db.commit()
        db.refresh(album)

        rights_service.create_rights(
            db,
            album_id=album.id,
            user_id=author_id,
            is_owner=True
        )
        return album

    def get_album(self, db: Session, album_id: UUID) -> Optional[models.Album]:
        return db.query(models.Album).filter(models.Album.id == album_id).first()

    def list_albums(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Album]:
        return db.query(models.Album).offset(skip).limit(limit).all()

    def update_album(self, db: Session, album_id: UUID, updated_data: schemas.AlbumUpdate, user: user_schemas.User) -> models.Album:
        album = self.get_album(db, album_id)
        if not album:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

        # The relationship in your model is not correct
        # You need to check the rights table for permissions
        # For now, we will check if the user is the author
        if str(album.owner_id) != str(user.id) and not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to edit this album")

        album.title = updated_data.title or album.title
        album.description = updated_data.description or album.description
        db.commit()
        db.refresh(album)
        return album

    def delete_album(self, db: Session, album_id: UUID, user: user_schemas.User) -> dict:
        album = self.get_album(db, album_id)
        if not album:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

        if str(album.owner_id) != str(user.id) and not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission to delete this album")

        db.delete(album)
        db.commit()
        return {"detail": "Album deleted successfully"}
    def add_image_to_album(self, db: Session, album_id: UUID, image_id: UUID):
        album = self.get_album(db, album_id)
        image = db.query(image_models.Image).filter_by(id=image_id).first()

        if not album or not image:
            raise ValueError("Album or Image not found")

        image.album_id = album_id
        db.commit()
        db.refresh(image)
        return image
