import os
import httpx
import asyncio
from fastapi import APIRouter, HTTPException

# ---------------------------------------------------------
# 👇 CHANGE THESE IMPORTS TO MATCH YOUR PROJECT STRUCTURE
# ---------------------------------------------------------
# If SessionLocal is in backend/app/db/database.py
from app.db.database import SessionLocal

# If your Image model is in backend/app/modules/models.py
from app.modules.images.models import Image
# ---------------------------------------------------------

router = APIRouter()

# URL where your week2ai generator service is running
GENERATOR_URL = "http://localhost:8001"

# Path to your gallery uploads folder
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


@router.post("/generate")
async def ai_generate(prompt: str):
    """
    Generate an image using the AI service and save it into the gallery DB.
    """
    async with httpx.AsyncClient() as client:
        # Step 1: send prompt to generator
        r = await client.post(f"{GENERATOR_URL}/generate", json={"prompt": prompt})
        if r.status_code != 200:
            raise HTTPException(500, "Generator service failed")
        job_id = r.json()["job_id"]

        # Step 2: poll until done
        for _ in range(30):  # 30 tries (~30s max)
            s = await client.get(f"{GENERATOR_URL}/status/{job_id}")
            data = s.json()

            if data["status"] == "done":
                result_url = GENERATOR_URL + data["result_url"]

                # Step 3: download image
                img_resp = await client.get(result_url)
                if img_resp.status_code != 200:
                    raise HTTPException(500, "Could not fetch generated image")

                fname = f"{job_id}.png"
                fpath = os.path.join(UPLOADS_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(img_resp.content)

                # Step 4: insert into DB
                db = SessionLocal()
                try:
                    # 👇 Change fields to match your Image model schema
                    img = Image(
                        filename=fname,
                        source="ai",   # remove if not in your model
                        prompt=prompt, # remove if not in your model
                    )
                    db.add(img)
                    db.commit()
                    db.refresh(img)
                    return {
                        "status": "done",
                        "filename": fname,
                        "id": img.id,
                    }
                finally:
                    db.close()

            elif data["status"] == "failed":
                raise HTTPException(500, "Generation failed")

            else:
                await asyncio.sleep(1)

        raise HTTPException(504, "Generation timed out")
