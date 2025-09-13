import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.modules.images import models as image_models
from app.modules.comments import models as comment_models

router = APIRouter(prefix="/gallery")

@router.get("/")
def get_gallery(request: Request, db: Session = Depends(get_db)):
    """
    Fetch all images with their likes, views, and comments.
    Returns full URLs for images so the frontend can display them directly.
    """
    images = (
        db.query(image_models.Image)
        .options(
            joinedload(image_models.Image.likes),
            joinedload(image_models.Image.views),
            joinedload(image_models.Image.comments).joinedload(comment_models.Comment.user),
        )
        .all()
    )

    base_url = str(request.base_url)  # e.g., http://localhost:8000/

    response = []
    for img in images:
        # ✅ Force SQLAlchemy to reload latest state from DB
        db.refresh(img)

        full_url = f"{base_url}static/uploads/{img.filename}"  # Match your StaticFiles mount

        # ✅ Always fresh counts
        likes_count = len(img.likes) if img.likes else 0
        views_count = len(img.views) if img.views else 0

        # Comments with safe user names
        comment_list = [
            {
                "id": comment.id,
                "text": comment.content,
                "user": comment.user.username if comment.user else "Anonymous",
            }
            for comment in img.comments
        ]

        response.append({
            "id": img.id,
            "url": full_url,
            "title": img.title,
            "album_id": img.album_id,
            "likes": likes_count,
            "views": views_count,
            "comments": comment_list,
        })

    return response
