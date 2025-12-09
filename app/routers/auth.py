from fastapi import APIRouter, Depends, Response, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..deps import get_db_session, get_current_user
from ..schemas.auth import SignUp, Login
from ..services import auth as auth_service
from ..models.user import User

router = APIRouter()


@router.post("/signup")
def signup(
    response: Response,
    nickname: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    user = auth_service.signup(SignUp(nickname=nickname, password=password), db)
    auth_service.set_session_cookie(response, user.id)
    return RedirectResponse(url="/", status_code=303)


@router.post("/login")
def login(
    response: Response,
    nickname: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    user = auth_service.login(Login(nickname=nickname, password=password), db)
    auth_service.set_session_cookie(response, user.id)
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(response: Response):
    auth_service.clear_session_cookie(response)
    return RedirectResponse(url="/", status_code=303)


@router.post("/nickname")
def change_nickname(
    response: Response,
    nickname: str = Form(...),
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    # ensure unique
    exists = db.exec(select(User).where(User.nickname == nickname)).first()
    if exists and exists.id != user.id:
        return RedirectResponse(url="/profiles/me?err=busy", status_code=303)
    user.nickname = nickname
    db.add(user)
    db.commit()
    db.refresh(user)
    # refresh session cookie to keep logged in with new nickname
    auth_service.set_session_cookie(response, user.id)
    return RedirectResponse(url=f"/profiles/{user.nickname}", status_code=303)
