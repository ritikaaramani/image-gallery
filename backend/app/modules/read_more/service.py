import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from app.modules.read_more import models, schemas


def get_settings(db: Session) -> Optional[models.ReadMoreSettings]:
    return db.query(models.ReadMoreSettings).first()


def create_settings(db: Session, settings: schemas.ReadMoreSettingsCreate) -> models.ReadMoreSettings:
    db_settings = models.ReadMoreSettings(**settings.model_dump())
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


def update_settings(db: Session, settings_update: schemas.ReadMoreSettingsCreate) -> models.ReadMoreSettings:
    db_settings = db.query(models.ReadMoreSettings).first()
    if not db_settings:
        # If settings don't exist, create them
        return create_settings(db, settings_update)

    db_settings.apply_to_feeds = settings_update.apply_to_feeds
    db_settings.default_text = settings_update.default_text
    db.commit()
    db.refresh(db_settings)
    return db_settings


def markup_post_text(db: Session, text: str, url: str = "#") -> str:
    settings = get_settings(db)
    default_text = settings.default_text if settings else "...more"

    # Split the text on the marker
    parts = text.split("<!--more-->", 1)

    if len(parts) > 1:
        preview, rest = parts[0], parts[1]
        more_text = default_text
    else:
        preview, rest = text, ""
        more_text = default_text

    return f"{preview}<a class='read_more' href='{url}'>{more_text}</a>"
