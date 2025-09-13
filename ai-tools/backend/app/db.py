# backend/app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default path for local dev (keeps working locally with SQLite)
DEFAULT_SQLITE_PATH = os.path.join(os.getcwd(), "data", "backend.db")
# Prefer environment DATABASE_URL if provided (Render will set this)
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_SQLITE_PATH}"

# SQLite needs check_same_thread False for SQLAlchemy + multiple threads
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# create engine with future=True recommended for SQLAlchemy 1.4+
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
