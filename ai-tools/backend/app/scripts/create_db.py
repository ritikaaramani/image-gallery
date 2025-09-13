# backend/app/scripts/create_db.py

from backend.app.db import engine, Base

# Import models so SQLAlchemy registers all tables with Base.
# Simply importing the module is enough.
import backend.app.models  # noqa: F401

print("Creating DB schema...")
Base.metadata.create_all(bind=engine)
print("Done.")
