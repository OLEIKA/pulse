from typing import Optional

from fastapi import Depends, HTTPException, status, Response
from passlib.context import CryptContext
from sqlmodel import Session, select
from itsdangerous import URLSafeSerializer

from ..config import settings
from ..deps import serializer
from ..models.user import User
from ..schemas.auth import SignUp, Login
from ..db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_session_cookie(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def signup(data: SignUp, db: Session) -> User:
    exists = db.exec(select(User).where(User.nickname == data.nickname)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname already taken")
    user = User(nickname=data.nickname, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(data: Login, db: Session) -> User:
    user = db.exec(select(User).where(User.nickname == data.nickname)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    return user


def set_session_cookie(response: Response, user_id: int) -> None:
    cookie_value = create_session_cookie(user_id)
    response.set_cookie(
        key=settings.session_cookie,
        value=cookie_value,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.session_cookie)
