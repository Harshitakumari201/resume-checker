from sqlmodel import SQLModel, create_engine, Session
from typing import Optional


SQLITE_URL = "sqlite:///./backend/database.db"

# Use check_same_thread=False for SQLite when using threads (uvicorn reload)
engine = create_engine(SQLITE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)


def save_processed_resume(file_name: Optional[str], raw_text: Optional[str], data: dict) -> int:
    """Convenience helper to persist a `ProcessedResume` record (models.py)."""
    from .models import ProcessedResume

    pr = ProcessedResume(file_name=file_name, raw_text=raw_text, data=data)
    with Session(engine) as session:
        session.add(pr)
        session.commit()
        session.refresh(pr)
    return pr.id
