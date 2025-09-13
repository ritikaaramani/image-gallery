# backend/app/router.py
import uuid
import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue
from typing import Optional
from backend.app.db import SessionLocal, get_db  # adjust if your project exposes get_db differently
from backend.app import crud
from backend.app.worker import generation_task as generation_task_callable


router = APIRouter()
router = APIRouter()

# Pydantic schema for incoming generate requests (adjust fields as required)
class GenerateRequest(BaseModel):
    prompt: str
    seed: Optional[int] = None
    width: int = 512
    height: int = 512
    steps: int = 20
    batch: int = 1
    provider: str = "replicate"
    base_url: Optional[str]=None
    extra: Optional[dict]=None

# Redis settings (use env or fallback)
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")

@router.post("/generate")
def create_generation(req: GenerateRequest, db: Session = Depends(get_db)):
    """
    Create a generation job: insert DB job row and enqueue a worker task.
    Returns job_id that can be polled via GET /generate/{job_id} (implement separately).
    """
    # create UUID job id
    job_id = str(uuid.uuid4())

    # normalize payload to JSON-serializable dict
    payload = req.dict()

    # If base_url was not passed, set a default
    if not payload.get("base_url"):
        payload["base_url"] = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    # Create DB job record via crud (make sure crud.create_job exists and accepts these args)
    try:
        crud.create_job(db, job_id, payload)   # your create_job should insert the row with status "queued"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job in DB: {e}")

    # Enqueue the background job in Redis (RQ)
    try:
        redis_conn = Redis.from_url(REDIS_URL)
        q = Queue("generations", connection=redis_conn)
        q.enqueue(generation_task_callable, job_id, payload)
    except Exception as e:
        # If enqueue fails, mark job failed in DB and return error
        try:
            crud.update_job_status(db, job_id, "failed", error=f"enqueue error: {e}")
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {e}")

    return JSONResponse(status_code=200, content={"job_id": job_id, "queued": True})

@router.get("/generate/{job_id}")
def get_generation_status(job_id: str, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "status": job.status,
        "error": job.error,
        "images": job.images,  # should contain list of { url, thumbnail, meta, nsfw }
    }