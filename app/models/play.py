from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Play(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    track_id: int = Field(foreign_key="track.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    played_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    track: Optional["Track"] = Relationship(back_populates="plays")
    user: Optional["User"] = Relationship(back_populates="plays")


from .track import Track  # noqa: E402
from .user import User  # noqa: E402
