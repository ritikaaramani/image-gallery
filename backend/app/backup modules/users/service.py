# app/modules/users/service.py
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.users import models, schemas
import uuid
import datetime
from typing import Optional

def create_user_service(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db_user = models.User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        password=hashed_password,
        avatar_image_id=user.avatar_image_id if getattr(user, "avatar_image_id", None) else None,
        is_admin=user.is_admin if getattr(user, "is_admin", None) else False,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Username or email already exists") from e
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == str(user_id)).first()

def delete_user(db: Session, user_id: str) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
