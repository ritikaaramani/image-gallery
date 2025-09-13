# backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import models module first so model classes are loaded and registered
# against the Base defined in backend.app.db
from backend.app import models  # noqa: F401 (import for side-effects)
from backend.app.router import router as api_router
from backend.app.db import engine, Base

app = FastAPI(title="AI Generator PoC")

# DEV convenience: create tables automatically if they don't exist.
# This must use the same Base that model classes inherit from (imported from db).
# Remove in production and use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

# Mount static folder for generated images
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
