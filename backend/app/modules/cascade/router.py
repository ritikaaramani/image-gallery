from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel
from .service import CascadeService
from app.modules.cascade import schemas
from app.modules.users.schemas import User as UserSchema
from app.auth.dependencies import get_current_user
from app.modules.cascade.permissions import can_change_settings


router = APIRouter(prefix="/cascade", tags=["Cascade"])
service = CascadeService()


@router.get("/settings", response_model=schemas.CascadeSettings)
def read_settings():
    return service.get_settings()


@router.post("/settings", response_model=schemas.CascadeSettings)
def update_settings(
    settings: schemas.CascadeSettings,
    user: UserSchema = Depends(get_current_user)
):
    if not can_change_settings(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")
    return service.update_settings(settings)
