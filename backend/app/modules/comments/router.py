# router.py
from fastapi import APIRouter, HTTPException, Depends, Body, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from fastapi.encoders import jsonable_encoder

from app.db.database import get_db
from app.modules.comments.service import CommentService
from app.modules.comments.schemas import CommentSchema
from app.modules.users.schemas import User as UserSchema
from app.auth.dependencies import get_current_user

# Correct prefix for the comments router
router = APIRouter(prefix="/comments", tags=["Comments"])

# -----------------------------
# Endpoints for Album Comments
# -----------------------------
@router.get("/albums/{album_id}", response_model=List[CommentSchema])
def list_album_comments(
    album_id: uuid.UUID, 
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comments = service.list_comments(db, parent_id=album_id)
    return jsonable_encoder(comments)

@router.post("/albums/{album_id}", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def add_album_comment(
    album_id: uuid.UUID,
    content: str = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comment = service.add_comment(
        db=db,
        parent_id=album_id,
        user_id=user.id,
        content=content,
    )
    return jsonable_encoder(comment)

# -----------------------------
# Endpoints for Image Comments
# -----------------------------
@router.get("/images/{image_id}", response_model=List[CommentSchema])
def list_image_comments(
    image_id: uuid.UUID, 
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comments = service.list_comments(db, parent_id=image_id)
    return jsonable_encoder(comments)

@router.post("/images/{image_id}", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def add_image_comment(
    image_id: uuid.UUID,
    content: str = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comment = service.add_comment(
        db=db,
        parent_id=image_id,
        user_id=user.id,
        content=content,
    )
    return jsonable_encoder(comment)

# -----------------------------
# Universal Comment Endpoints (Update/Delete)
# -----------------------------
@router.put("/{comment_id}", response_model=CommentSchema)
def update_comment(
    comment_id: uuid.UUID,
    updated_content: str = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comment = service.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        
    if str(comment.user_id) != str(user.id) and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    updated_comment = service.update_comment(
        db, 
        comment_id=comment_id, 
        updated_content=updated_content
    )
    return jsonable_encoder(updated_comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: uuid.UUID, 
    user: UserSchema = Depends(get_current_user), 
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    comment = service.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if str(comment.user_id) != str(user.id) and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    service.delete_comment(db, comment_id=comment_id)


@router.delete("/admin/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_comment(
    comment_id: uuid.UUID, 
    user: UserSchema = Depends(get_current_user), 
    db: Session = Depends(get_db),
    service: CommentService = Depends(CommentService) # Injected service
):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    service.delete_comment(db, comment_id=comment_id)
