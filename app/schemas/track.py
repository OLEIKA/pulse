from typing import Optional
from datetime import datetime
from pydantic import BaseModel, constr


class TrackBase(BaseModel):
    title: constr(min_length=1, max_length=120)
    artist: constr(min_length=0, max_length=120) | None = ""


class TrackCreate(TrackBase):
    pass


class TrackUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=120)] = None
    artist: Optional[constr(min_length=0, max_length=120)] = None


class TrackRead(TrackBase):
    id: int
    creator_id: int
    creator_nickname: str
    is_platform: bool = False
    likes_count: int = 0
    plays_count: int = 0
    created_at: datetime

    class Config:
        orm_mode = True
