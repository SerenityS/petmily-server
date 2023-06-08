from datetime import datetime
from typing import Optional

from app.db import Base
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column


class HistoryDB(Base):
    __tablename__ = "history"

    id: Mapped[int] = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False)
    chip_id: Mapped[str] = mapped_column(
        String(length=100), index=False, nullable=False
    )
    consume: Mapped[int] = mapped_column(Integer, index=False, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())


class History(BaseModel):
    id: Optional[int]
    user_id: str
    chip_id: str
    consume: int
    date: Optional[datetime]
