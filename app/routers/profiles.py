from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..deps import get_db_session, get_current_user
from ..models.user import User
from ..models.track import Track
from ..models.favorite import Favorite
from ..routers.tracks import aggregate_track_counts

router = APIRouter()


def get_user_by_nickname(db: Session, nickname: str) -> User:
    user = db.exec(select(User).where(User.nickname == nickname)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me")
def my_profile(db: Session = Depends(get_db_session), user: User = Depends(get_current_user)):
    uploaded = db.exec(select(Track).where(Track.creator_id == user.id)).all()
    favorite_ids = [fav.track_id for fav in db.exec(select(Favorite).where(Favorite.user_id == user.id)).all()]
    favorites = db.exec(select(Track).where(Track.id.in_(favorite_ids))).all() if favorite_ids else []
    return {
        "user": {"id": user.id, "nickname": user.nickname},
        "uploaded": aggregate_track_counts(db, uploaded),
        "favorites": aggregate_track_counts(db, favorites),
    }


@router.get("/{nickname}")
def profile(nickname: str, db: Session = Depends(get_db_session)):
    user = get_user_by_nickname(db, nickname)
    uploaded = db.exec(select(Track).where(Track.creator_id == user.id)).all()
    favorite_ids = [fav.track_id for fav in db.exec(select(Favorite).where(Favorite.user_id == user.id)).all()]
    favorites = db.exec(select(Track).where(Track.id.in_(favorite_ids))).all() if favorite_ids else []
    return {
        "user": {"id": user.id, "nickname": user.nickname},
        "uploaded": aggregate_track_counts(db, uploaded),
        "favorites": aggregate_track_counts(db, favorites),
    }
