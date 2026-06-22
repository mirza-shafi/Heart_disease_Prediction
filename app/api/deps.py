from typing import Generator
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal, get_db
from app.db.models import User
from app.core.config import settings

security = HTTPBearer()

def get_current_user(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

security_optional = HTTPBearer(auto_error=False)

def get_current_user_optional(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security_optional)) -> User:
    if not credentials:
        return None
    try:
        return get_current_user(db, credentials)
    except HTTPException:
        return None
