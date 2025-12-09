from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: str = Field(index=True, unique=True, max_length=50)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tracks: List["Track"] = Relationship(back_populates="creator")
    favorites: List["Favorite"] = Relationship(back_populates="user")
    plays: List["Play"] = Relationship(back_populates="user")


# Import hints for type checking / relationships
from .track import Track  # noqa: E402
from .favorite import Favorite  # noqa: E402
from .play import Play  # noqa: E402
