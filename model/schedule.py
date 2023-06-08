from app.db import Base
from pydantic import BaseModel, Field
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class ScheduleDB(Base):
    __tablename__ = "schedule"

    chip_id: Mapped[str] = mapped_column(
        String(length=100), primary_key=True, index=False, nullable=False
    )
    schedule_json: Mapped[str] = mapped_column(
        String(length=1500), index=False, nullable=False
    )


class Schedule(BaseModel):
    chip_id: str
    schedule_json: str
