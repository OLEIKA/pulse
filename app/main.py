from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .config import settings
from .db import create_db_and_tables
from .db import engine
from .routers import auth, tracks, profiles, pages
from .models.user import User
from .models.track import Track
from pathlib import Path

app = FastAPI(title=settings.app_name)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    seed_platform_user_and_tracks()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(pages.router, tags=["pages"])


def seed_platform_user_and_tracks() -> None:
    """Create platform user and import mp3 files from static/uploads/platform as 'original' tracks."""
    platform_uploads = Path("app/static/uploads/platform")
    with Session(engine) as session:
        platform_user = session.exec(select(User).where(User.nickname == "Platform")).first()
        if not platform_user:
            platform_user = User(nickname="Platform", hashed_password="platform")
            session.add(platform_user)
            session.commit()
            session.refresh(platform_user)

        if platform_uploads.exists():
            for mp3_file in platform_uploads.glob("*.mp3"):
                exists = session.exec(select(Track).where(Track.filename == f"platform/{mp3_file.name}")).first()
                if exists:
                    continue
                track = Track(
                    title=mp3_file.stem,
                    artist="",
                    filename=f"platform/{mp3_file.name}",
                    creator_id=platform_user.id,
                    is_platform=True,
                )
                session.add(track)
            session.commit()
