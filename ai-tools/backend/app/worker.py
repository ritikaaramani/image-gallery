# backend/app/worker.py
import os
from datetime import datetime
from uuid import uuid4

from backend.app.db import SessionLocal
from backend.app import crud
from backend.app.utils import save_image_bytes, make_thumbnail, simple_safety_check

# Only use the Replicate provider for this PoC
from backend.app.providers.replicate_provider import ReplicateProvider

def generation_task(job_db_id: str, payload: dict):
    """
    RQ worker entry point.
    job_db_id: id of GenerationJob in DB
    payload: dict with prompt, seed, width, height, steps, batch, etc.
    """
    db = SessionLocal()
    try:
        crud.update_job_status(db, job_db_id, "running")
        # choose provider; default to replicate
        provider_name = (payload.get("provider") or "replicate").lower()
        if provider_name != "replicate":
            # reject unsupported provider for now
            raise RuntimeError(f"Unsupported provider '{provider_name}'. This worker only supports 'replicate'.")

        prov = ReplicateProvider()  # reads token/version from env
        results = prov.generate(
            prompt=payload.get("prompt"),
            seed=payload.get("seed"),
            width=payload.get("width", 512),
            height=payload.get("height", 512),
            steps=payload.get("steps", 20),
            batch=payload.get("batch", 1),
            extra=payload.get("extra", {})
        )

        # Persist each artifact returned by provider
        for i, art in enumerate(results):
            # filename: jobid_index.png
            fn = f"{job_db_id}_{i}.png"
            save_image_bytes(art["bytes"], fn)
            thumb_path = make_thumbnail(art["bytes"], f"{job_db_id}_{i}_thumb.jpg")

            base_url = payload.get("base_url", os.getenv("BASE_URL", "http://127.0.0.1:8000"))
            url = f"{base_url}/generated/{fn}"
            thumb_url = f"{base_url}/generated/thumbs/{os.path.basename(thumb_path)}"

            safety = simple_safety_check(art["bytes"])

            img = crud.create_image_record(
                db,
                job_db_id,
                fn,
                url,
                thumb_url,
                meta=art.get("meta", {}),
                nsfw=safety.get("nsfw", False)
            )

            crud.append_job_image(db, job_db_id, {
                "image_id": img.id,
                "url": url,
                "thumbnail": thumb_url,
                "meta": img.meta,
                "nsfw": img.nsfw
            })

        crud.update_job_status(db, job_db_id, "success")
    except Exception as e:
        # ensure the error is stored for debugging
        crud.update_job_status(db, job_db_id, "failed", error=str(e))
    finally:
        db.close()
