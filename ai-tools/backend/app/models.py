# backend/app/models.py
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, func
from sqlalchemy import Boolean
from backend.app.db import Base


import uuid

def gen_uuid():
    return str(uuid.uuid4())

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), nullable=True)
    prompt = Column(Text, nullable=False)
    seed = Column(Integer, nullable=True)
    width = Column(Integer, default=512)
    height = Column(Integer, default=512)
    steps = Column(Integer, default=20)
    batch = Column(Integer, default=1)
    model = Column(String(200), nullable=True)
    provider = Column(String(100), nullable=False, default="automatic1111")
    status = Column(String(30), default="queued")  # queued, running, success, failed, aborted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(Text, nullable=True)
    # images: list of saved images metadata
    images = Column(JSON, nullable=True)
    extra = Column(JSON, nullable=True)


class GeneratedImage(Base):
    __tablename__ = "generated_images"
    id = Column(String(36), primary_key=True, default=gen_uuid)
    job_id = Column(String(36), nullable=False)
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    thumbnail = Column(String(500), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, nullable=True)
    nsfw = Column(Boolean, default=False)
