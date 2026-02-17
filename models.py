from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class ProcessedResume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    raw_text: Optional[str] = None
    data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
