# app/modules/users/router.py
import uuid as _uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.modules.users import schemas, service
from app.modules.maptcha.service import verify_maptcha
from app.auth import service as auth_service
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import uuid
from app.auth.dependencies import get_current_user
from app.modules.users.schemas import User as UserSchema

router = APIRouter( prefix="/users",tags=["Users"])

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=schemas.UserOut, status_code=201)
def create_user_endpoint(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    # Optional captcha validation if provided by client
    if user.maptcha_response is not None or user.maptcha_challenge is not None:
        if not verify_maptcha(
            user.maptcha_response,
            user.maptcha_requested,
            user.maptcha_challenge,
        ):
            raise HTTPException(status_code=400, detail="Invalid captcha")
    try:
        db_user = service.create_user_service(db, user)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    return db_user

@router.get("/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_users(db=db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = service.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=schemas.UserOut)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = service.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: str,
    user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    db_user = service.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return


