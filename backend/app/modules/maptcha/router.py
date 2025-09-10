from fastapi import APIRouter, HTTPException
from .service import generate_challenge, verify_maptcha
from app.modules.maptcha.schemas import MaptchaCheckRequest
from app.modules.maptcha import service

router = APIRouter(prefix="/maptcha", tags=["maptcha"])

@router.get("/generate")
def generate():
    return generate_challenge()

@router.post("/check")
def check_maptcha(data: MaptchaCheckRequest): # <-- Use the schema as the parameter
    try:
        is_correct = service.verify_maptcha(data.maptcha_response, data.maptcha_requested, data.maptcha_challenge)
        if is_correct:
            return {"detail": "Maptcha check successful"}
        else:
            raise HTTPException(status_code=400, detail="Maptcha check failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

