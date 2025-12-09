from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Track(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=120)
    artist: str = Field(default="", max_length=120)
    filename: str  # stored file path/filename
    creator_id: int = Field(foreign_key="user.id", index=True)
    is_platform: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    creator: Optional["User"] = Relationship(back_populates="tracks")
    favorites: List["Favorite"] = Relationship(back_populates="track")
    plays: List["Play"] = Relationship(back_populates="track")


from .user import User  # noqa: E402
from .favorite import Favorite  # noqa: E402
from .play import Play  # noqa: E402
