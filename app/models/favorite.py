from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Favorite(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    track_id: int = Field(foreign_key="track.id", primary_key=True)

    user: Optional["User"] = Relationship(back_populates="favorites")
    track: Optional["Track"] = Relationship(back_populates="favorites")


from .user import User  # noqa: E402
from .track import Track  # noqa: E402
