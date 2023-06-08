from app.db import Base
from pydantic import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class DeviceDataDB(Base):
    __tablename__ = "device_data"

    chip_id: Mapped[str] = mapped_column(
        String(length=100), primary_key=True, unique=True, index=False, nullable=False
    )
    bowl_amount: Mapped[int] = mapped_column(Integer, index=False, nullable=False)
    feed_box_amount: Mapped[int] = mapped_column(Integer, index=False, nullable=False)


class DeviceData(BaseModel):
    chip_id: str
    bowl_amount: int
    feed_box_amount: int
