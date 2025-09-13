# backend/app/crud.py
from sqlalchemy.orm import Session
from backend.app import models
from datetime import datetime
import json

def create_job(db: Session, job_id: str, payload: dict):
    job = models.GenerationJob(
        id=job_id,
        prompt=payload.get("prompt"),
        seed=payload.get("seed"),
        width=payload.get("width", 512),
        height=payload.get("height", 512),
        steps=payload.get("steps", 20),
        batch=payload.get("batch", 1),
        model=payload.get("model"),
        provider=payload.get("provider", "automatic1111"),
        status="queued",
        extra=payload.get("extra", {})
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def update_job_status(db: Session, job_id: str, status: str, error: str = None):
    job = db.query(models.GenerationJob).filter(models.GenerationJob.id == job_id).first()
    if not job:
        return None
    job.status = status
    if status == "running":
        job.started_at = datetime.utcnow()
    if status in ("success", "failed", "aborted"):
        job.finished_at = datetime.utcnow()
    if error:
        job.error = error
    db.commit()
    db.refresh(job)
    return job

def append_job_image(db: Session, job_id: str, image_record: dict):
    job = db.query(models.GenerationJob).filter(models.GenerationJob.id == job_id).first()
    if not job:
        return None
    imgs = job.images or []
    imgs.append(image_record)
    job.images = imgs
    db.commit()
    db.refresh(job)
    return job

def create_image_record(db: Session, job_id: str, filename: str, url: str, thumbnail: str, meta: dict, nsfw: bool=False):
    img = models.GeneratedImage(
        job_id=job_id,
        filename=filename,
        url=url,
        thumbnail=thumbnail,
        meta=meta,
        nsfw=nsfw
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    return img

def get_job(db: Session, job_id: str):
    return db.query(models.GenerationJob).filter(models.GenerationJob.id == job_id).first()
