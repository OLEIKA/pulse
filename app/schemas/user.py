from datetime import datetime
from typing import List
from pydantic import BaseModel, constr


class UserRead(BaseModel):
    id: int
    nickname: constr(max_length=50)
    created_at: datetime

    class Config:
        orm_mode = True


class Profile(BaseModel):
    user: UserRead
    uploaded_track_ids: List[int]
    favorite_track_ids: List[int]
