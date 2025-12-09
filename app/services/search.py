from typing import List, Optional

from sqlmodel import Session, select

from ..models.track import Track
from ..models.user import User


def search_tracks(db: Session, query: Optional[str], filter_by: str = "all") -> List[Track]:
    stmt = select(Track)
    if filter_by == "user":
        stmt = stmt.where(Track.is_platform == False)  # noqa: E712
    elif filter_by == "platform":
        stmt = stmt.where(Track.is_platform == True)  # noqa: E712

    if query:
        pattern = f"%{query}%"
        stmt = stmt.where(Track.title.ilike(pattern))

    stmt = stmt.order_by(Track.created_at.desc()).limit(50)
    return db.exec(stmt).all()


def search_profiles(db: Session, nickname_query: Optional[str]) -> List[User]:
    if not nickname_query:
        return []
    pattern = f"%{nickname_query}%"
    stmt = select(User).where(User.nickname.ilike(pattern)).limit(20)
    return db.exec(stmt).all()
