import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.db.database import get_db
from app.modules.images import models as image_models
from app.modules.image_likes import models as like_models
from app.modules.image_views import models as view_models
from app.modules.comments import models as comment_models
from app.modules.users import models as user_models

router = APIRouter(prefix="/gallery")

@router.get("/")
def get_gallery(request: Request, db: Session = Depends(get_db)):
    # Use joinedload to fetch all related data in a single query,
    # solving the N+1 query problem.
    images = db.query(image_models.Image)\
        .options(
            joinedload(image_models.Image.likes),
            joinedload(image_models.Image.views),
            joinedload(image_models.Image.comments).joinedload(comment_models.Comment.user)
        ).all()

    response = []
    for img in images:
        # Build full URL using request
        base_url = str(request.base_url)
        full_url = f"{base_url}uploads/{img.filename}"

        # Get counts from the pre-loaded data
        likes_count = len(img.likes)
        views_count = len(img.views)

        # Unpack comments and user info from pre-loaded data
        comment_list = [
            {"id": comment.id, "text": comment.content, "user": comment.user.username}
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
