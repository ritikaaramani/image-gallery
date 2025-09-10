from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional, List

from app.modules.images import models, schemas
from app.modules.image_likes import models as likes_models
from app.modules.image_views import models as image_views_models
from app.modules.uploads import models as uploads_models


class ImageService:
    def create_image_from_upload(
        self,
        db: Session,
        upload_id: UUID,
        title: str,
        caption: Optional[str],
        privacy: str,
        license: Optional[str],
        author_id: str,
    ) -> models.Image:
        # Check if the upload exists
        upload = db.query(uploads_models.Upload).filter_by(id=upload_id).first()
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found"
            )

        # Check if an Image has already been created for this upload
        if upload.image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An image already exists for this upload",
            )

        # Create the new Image record and link it to the Upload record
        new_image = models.Image(
            title=title,
            caption=caption,
            privacy=privacy,
            license=license,
            author_id=author_id,
            upload_id=upload.id,  # Link to the existing upload
            filename=upload.filename,  # ✅ populate from Upload
            mime_type=upload.content_type,  # ✅ populate from Upload
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        return new_image

    def get_image(self, db: Session, image_id: UUID) -> Optional[models.Image]:
        return (
            db.query(models.Image)
            .options(joinedload(models.Image.upload))  # eager load Upload
            .filter(models.Image.id == image_id)
            .first()
        )

    def list_images(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.Image]:
        return db.query(models.Image).filter(models.Image.id != None).offset(skip).limit(limit).all()

    def delete_image(self, db: Session, image_id: UUID, user):
        image = self.get_image(db, image_id)
        if not image:
            return None  # Return None if image not found
        if str(image.author_id) != str(user.id) and not getattr(user, "is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete the associated upload record as well
        if image.upload:
            db.delete(image.upload)

        db.delete(image)
        db.commit()
        return True  # Return True for success

    def like_image(self, db: Session, image_id: UUID, user_id: str):
        existing_like = (
            db.query(likes_models.ImageLike)
            .filter_by(image_id=image_id, user_id=user_id)
            .first()
        )
        if existing_like:
            raise HTTPException(
                status_code=400, detail="User already liked this image"
            )
        like = likes_models.ImageLike(image_id=image_id, user_id=user_id)
        db.add(like)
        db.commit()
        db.refresh(like)

    def record_view(self, db: Session, image_id: UUID):
        image = self.get_image(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        view = image_views_models.ImageView(image_id=image_id, user_id=None)
        db.add(view)
        db.commit()
        db.refresh(view)
