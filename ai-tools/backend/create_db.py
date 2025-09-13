# backend/create_db.py
"""
Create DB tables for local development.
Run: python backend/create_db.py
"""
from backend.app import models   # imports model classes and ensures they are registered
from backend.app.db import Base, engine

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created.")
