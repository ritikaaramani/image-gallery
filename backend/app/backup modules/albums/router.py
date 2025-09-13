from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.modules.albums import schemas, service
from app.auth.dependencies import get_current_user
from app.modules.users import schemas as user_schemas
from app.modules.images import schemas as image_schemas
from app.modules.albums.service import AlbumService
from app.modules.users.schemas import User as UserSchema

router = APIRouter(prefix="/albums", tags=["Albums"])
album_service = service.AlbumService()


@router.get("/", response_model=List[schemas.Album])
def list_albums(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return album_service.list_albums(db, skip, limit)


@router.get("/{album_id}", response_model=schemas.Album)
def get_album(album_id: UUID, db: Session = Depends(get_db)):
    album = album_service.get_album(db, album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")
    return album


@router.post("/", response_model=schemas.Album, status_code=status.HTTP_201_CREATED)
def create_album(
    album: schemas.AlbumCreate,
    user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return album_service.create_album(db, album, user.id)


@router.put("/{album_id}", response_model=schemas.Album)
def update_album(
    album_id: UUID,
    updated: schemas.AlbumUpdate,
    user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return album_service.update_album(db, album_id, updated, user)


@router.delete("/{album_id}")
def delete_album(
    album_id: UUID,
    user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return album_service.delete_album(db, album_id, user)

@router.post("/{album_id}/images/{image_id}", response_model=image_schemas.ImageResponse)
def add_image_to_album_endpoint(
    album_id: UUID,
    image_id: UUID,
    db: Session = Depends(get_db),
    service: AlbumService = Depends(AlbumService)
):
    try:
        return service.add_image_to_album(db, album_id, image_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/admin/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_album(
    album_id: UUID,
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    deleted = AlbumService.delete_album(db, album_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")
    return

