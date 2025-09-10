# app/modules/image_likes/router.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from uuid import UUID
from typing import List
from app.auth.dependencies import get_current_user
from app.modules.users.schemas import User as UserSchema
from app.modules.images import schemas as image_schemas
from app.modules.image_likes.service import LikesService

router = APIRouter(prefix="/likes", tags=["Likes"])

# Dependency to get service instance
def get_likes_service() -> LikesService:
    return LikesService()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_like_endpoint(
    image_id: UUID = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    service: LikesService = Depends(get_likes_service)
):
    """Add a like to an image"""
    try:
        return service.add_like(image_id, user.id)
    except HTTPException:
        raise  # Re-raise HTTP exceptions from service
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add like: {str(e)}"
        )

@router.delete("/", status_code=status.HTTP_200_OK)  # Changed from 204 to 200 to return message
def remove_like_endpoint(
    image_id: UUID = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    service: LikesService = Depends(get_likes_service)
):
    """Remove a like from an image"""
    try:
        deleted = service.remove_like(image_id, user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Like not found or already removed"
            )
        return {"message": "Like removed successfully"}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove like: {str(e)}"
        )

@router.get("/count/{image_id}")
def get_likes_count_endpoint(
    image_id: UUID, 
    service: LikesService = Depends(get_likes_service)
):
    """Get the total number of likes for an image"""
    try:
        count = service.get_likes_count(image_id)
        return {
            "image_id": str(image_id),
            "count": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get likes count: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[image_schemas.ImageResponse])
def get_liked_images_endpoint(
    user_id: UUID, 
    service: LikesService = Depends(get_likes_service)
):
    """Get all images liked by a specific user"""
    try:
        return service.get_liked_images(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get liked images: {str(e)}"
        )

# Additional helpful endpoints
@router.get("/check/{image_id}")
def check_if_liked_endpoint(
    image_id: UUID,
    user: UserSchema = Depends(get_current_user),
    service: LikesService = Depends(get_likes_service)
):
    """Check if current user has liked a specific image"""
    try:
        is_liked = service.is_liked_by_user(image_id, user.id)
        return {
            "image_id": str(image_id),
            "user_id": str(user.id),
            "is_liked": is_liked
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check like status: {str(e)}"
        )

@router.get("/user/me", response_model=List[image_schemas.ImageResponse])
def get_my_liked_images_endpoint(
    user: UserSchema = Depends(get_current_user),
    service: LikesService = Depends(get_likes_service)
):
    """Get all images liked by the current user"""
    try:
        return service.get_liked_images(user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get your liked images: {str(e)}"
        )

# Toggle endpoint (more user-friendly)
@router.post("/toggle", status_code=status.HTTP_200_OK)
def toggle_like_endpoint(
    image_id: UUID = Body(..., embed=True),
    user: UserSchema = Depends(get_current_user),
    service: LikesService = Depends(get_likes_service)
):
    """Toggle like status for an image (add if not liked, remove if liked)"""
    try:
        is_liked = service.is_liked_by_user(image_id, user.id)
        
        if is_liked:
            # Remove like
            deleted = service.remove_like(image_id, user.id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to remove like"
                )
            return {
                "message": "Like removed",
                "action": "removed",
                "is_liked": False,
                "image_id": str(image_id)
            }
        else:
            # Add like
            result = service.add_like(image_id, user.id)
            return {
                "message": "Like added",
                "action": "added", 
                "is_liked": True,
                "image_id": str(image_id),
                "like": result.get("like")
            }
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle like: {str(e)}"
        )
