from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DeviceDB(Base):
    __tablename__ = "device"

    id: Mapped[int] = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(length=100), index=False, nullable=False)
    chip_id: Mapped[str] = mapped_column(
        String(length=300), index=False, nullable=False
    )
    pass


class Device(BaseModel):
    user_id: str
    name: str
    chip_id: str
