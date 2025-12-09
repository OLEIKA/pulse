from sqlmodel import SQLModel, create_engine, Session

from .config import settings

# SQLite для MVP, check_same_thread=False чтобы шарить соединение в Uvicorn
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
