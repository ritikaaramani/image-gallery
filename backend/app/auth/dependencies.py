from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.users import models as user_models
from app.modules.users.schemas import User as UserSchema

# This is a placeholder for your JWT secret key
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# This dependency gets the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(user_models.User).filter_by(id=user_id).first()
    if user is None:
        raise credentials_exception
    return user
