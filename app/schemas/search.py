from typing import Optional
from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: Optional[str] = None
    profile: Optional[str] = None
