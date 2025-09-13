# app/modules/users/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=1)
    email: EmailStr
    maptcha_response: Optional[int] = None
    maptcha_requested: Optional[int] = None
    maptcha_challenge: Optional[str] = None
    avatar_image_id: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: Optional[bool] = False

class User(UserBase):
    id: str
    created_at: datetime
    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar_image_id: Optional[str] = None
    is_admin: bool = False
    created_at: datetime
    class Config:
        orm_mode = True
        json_encoders = {
            uuid.UUID: str
        }
