# app/modules/images/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.modules.images import schemas, service
from app.modules.users import schemas as user_schemas
from app.auth.dependencies import get_current_user
from app.modules.images.service import ImageService
from app.modules.users.schemas import User as UserSchema

router = APIRouter(prefix="/images", tags=["Images"])

# A single instance of the service
image_service = service.ImageService()

# ------------------ List all images ------------------
@router.get("/", response_model=List[schemas.ImageResponse])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return image_service.list_images(db, skip, limit)

# ------------------ Get single image ------------------
@router.get("/{image_id}", response_model=schemas.ImageResponse)
def get_image(image_id: UUID, db: Session = Depends(get_db)):
    service = ImageService()
    image = service.get_image(db, image_id)   # ✅ call method on service
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

# ------------------ Create image from upload ------------------
@router.post("/", response_model=schemas.ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    title: str = Form(...),
    caption: Optional[str] = Form(""),
    privacy: str = Form("public"),
    license: Optional[str] = Form(""),
    upload_id: UUID = Form(...), # Now takes an upload_id
    user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        new_image = image_service.create_image_from_upload(
            db=db,
            title=title,
            caption=caption,
            privacy=privacy,
            license=license,
            upload_id=upload_id,
            author_id=user.id
        )
        return new_image
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ------------------ Delete image ------------------
@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: UUID,
    user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted = image_service.delete_image(db, image_id, user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return

# ------------------ Like an image ------------------
@router.post("/{image_id}/like")
def like_image(image_id: UUID, user: user_schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    image_service.like_image(db, image_id, user.id)
    return {"message": "Image liked"}

# ------------------ Record a view ------------------
@router.post("/{image_id}/view")
def view_image(image_id: UUID, db: Session = Depends(get_db)):
    image_service.record_view(db, image_id)
    return {"message": f"View recorded for image '{image_id}'"}

@router.delete("/admin/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_image(
    image_id: UUID,
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    deleted = image_service.delete_image(db, image_id, user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return
