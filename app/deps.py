from fastapi import Depends, HTTPException, status, Cookie
from sqlmodel import Session, select
from itsdangerous import URLSafeSerializer, BadSignature

from .config import settings
from .db import get_session
from .models.user import User

serializer = URLSafeSerializer(settings.secret_key, salt="session")


def get_db_session(session: Session = Depends(get_session)) -> Session:
    return session


def get_current_user(
    session_data: str | None = Cookie(default=None, alias=settings.session_cookie),
    db: Session = Depends(get_db_session),
) -> User:
    if not session_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = serializer.loads(session_data)
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session payload")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(
    session_data: str | None = Cookie(default=None, alias=settings.session_cookie),
    db: Session = Depends(get_db_session),
) -> User | None:
    if not session_data:
        return None
    try:
        payload = serializer.loads(session_data)
    except BadSignature:
        return None
    user_id = payload.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)
