from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Music Platform"
    secret_key: str = "change-me"  # override via .env
    session_cookie: str = "music_session"
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parent.parent / 'music.db')}"

    class Config:
        env_file = ".env"


settings = Settings()
