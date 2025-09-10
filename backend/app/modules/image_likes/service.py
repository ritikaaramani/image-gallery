# app/modules/image_likes/service.py
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from app.db.supabase_client import supabase
from app.modules.images import schemas as image_schemas


class LikesService:
    def add_like(self, image_id: UUID, user_id: UUID):
        try:
            # Check if like already exists
            res = (
                supabase.table("likes")
                .select("id")
                .eq("image_id", str(image_id))
                .eq("user_id", str(user_id))
                .execute()
            )
            if res.data and len(res.data) > 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image already liked by this user")
            
            # Insert like
            insert_res = (
                supabase.table("likes")
                .insert({"image_id": str(image_id), "user_id": str(user_id)})
                .execute()
            )
            if not insert_res.data:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add like")
            
            return {"message": "Image liked", "like": insert_res.data[0]}

        except APIError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"API Error: {e.message}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

    def remove_like(self, image_id: UUID, user_id: UUID) -> bool:
        try:
            res = (
                supabase.table("likes")
                .delete()
                .eq("image_id", str(image_id))
                .eq("user_id", str(user_id))
                .execute()
            )
            return bool(res.data and len(res.data) > 0)
        except APIError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"API Error: {e.message}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

    def get_likes_count(self, image_id: UUID) -> int:
        try:
            res = (
                supabase.table("likes")
                .select("id")
                .eq("image_id", str(image_id))
                .execute()
            )
            count = len(res.data) if res.data else 0
            return count
        except APIError as e:
            print(f"Error getting likes count from Supabase: {e}")
            return 0
        except Exception as e:
            print(f"An unexpected error occurred while getting likes count: {e}")
            return 0

    def get_liked_images(self, user_id: UUID) -> List[image_schemas.ImageResponse]:
        try:
            # Get liked image IDs
            res = (
                supabase.table("likes")
                .select("image_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            
            image_ids = [row["image_id"] for row in (res.data or [])]
            if not image_ids:
                return []

            # Fetch image details in bulk
            images_res = (
                supabase.table("images")
                .select("*")
                .in_("id", image_ids)
                .execute()
            )
            return images_res.data or []
            
        except APIError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"API Error: {e.message}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

    def is_liked_by_user(self, image_id: UUID, user_id: UUID) -> bool:
        try:
            res = (
                supabase.table("likes")
                .select("id")
                .eq("image_id", str(image_id))
                .eq("user_id", str(user_id))
                .limit(1)
                .execute()
            )
            return bool(res.data and len(res.data) > 0)
        except APIError as e:
            print(f"Error checking if image is liked: {e}")
            return False
        except Exception as e:
            print(f"Error checking if image is liked: {e}")
            return False
