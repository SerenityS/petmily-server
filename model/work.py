from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class WorkDB(Base):
    __tablename__ = "work"

    id: Mapped[int] = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False)
    work: Mapped[str] = mapped_column(String(length=100), index=False, nullable=False)
    pass


class Work(BaseModel):
    id: int
    user_id: str
    work: str
