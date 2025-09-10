from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from typing import Optional

from app.modules.rights import models, schemas


class RightsService:
    def create_rights(
        self, db: Session, album_id: str, user_id: str,is_owner: bool,
        can_view: bool = True, can_edit: bool = False, can_delete: bool = False
    ) -> models.Rights:
        new_rights = models.Rights(
            album_id=album_id,
            user_id=user_id,
            can_view=can_view,
            can_edit=can_edit,
            can_delete=can_delete
        )
        db.add(new_rights)
        db.commit()
        db.refresh(new_rights)
        return new_rights

    def get_rights(self, db: Session, rights_id: UUID) -> Optional[models.Rights]:
        return db.query(models.Rights).filter(models.Rights.id == rights_id).first()

    def update_rights(self, db: Session, rights_id: UUID, update_data: schemas.RightsUpdate) -> models.Rights:
        rights = self.get_rights(db, rights_id)
        if not rights:
            raise HTTPException(status_code=404, detail="Rights not found")

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(rights, key, value)

        db.commit()
        db.refresh(rights)
        return rights

    def delete_rights(self, db: Session, rights_id: UUID) -> bool:
        rights = self.get_rights(db, rights_id)
        if not rights:
            return False

        db.delete(rights)
        db.commit()
        return True
