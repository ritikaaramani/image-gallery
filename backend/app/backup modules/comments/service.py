# service.py
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.modules.comments import models as comment_models
from app.modules.comments import schemas as comment_schemas
from app.modules.albums.models import Album # Added Album model import
from app.modules.images.models import Image # Added Image model import

class CommentService:
    """
    Service layer for handling all comment-related business logic.
    """

    def get_comment(self, db: Session, comment_id: uuid.UUID) -> Optional[comment_models.Comment]:
        """
        Retrieves a single comment by its ID.
        """
        return db.query(comment_models.Comment).filter_by(id=comment_id).first()

    def list_comments(self, db: Session, parent_id: uuid.UUID, limit: int = 100) -> List[comment_models.Comment]:
        """
        Lists all comments for a specific parent (album or image).
        """
        return db.query(comment_models.Comment).filter(
            (comment_models.Comment.album_id == parent_id) | (comment_models.Comment.image_id == parent_id)
        ).limit(limit).all()

    def add_comment(
        self,
        db: Session,
        parent_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str
    ) -> comment_models.Comment:
        """
        Creates and adds a new comment to the database for a specific parent.
        """
        # Determine if the parent is an album or an image
        if db.query(Album).filter_by(id=parent_id).first():
            new_comment = comment_models.Comment(
                album_id=parent_id,
                user_id=user_id,
                content=content,
            )
        elif db.query(Image).filter_by(id=parent_id).first():
            new_comment = comment_models.Comment(
                image_id=parent_id,
                user_id=user_id,
                content=content,
            )
        else:
            # Handle case where parent_id is not found in either table
            raise ValueError("Parent (album or image) not found.")
            
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment
    
    def update_comment(self, db: Session, comment_id: uuid.UUID, updated_content: str) -> Optional[comment_models.Comment]:
        comment = self.get_comment(db, comment_id)
        if comment:
            comment.content = updated_content
            db.commit()
            db.refresh(comment)
        return comment

    def delete_comment(self, db: Session, comment_id: uuid.UUID):
        """
        Deletes a comment by its ID.
        """
        comment = self.get_comment(db, comment_id)
        if comment:
            db.delete(comment)
            db.commit()
