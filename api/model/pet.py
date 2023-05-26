from typing import Optional

from app.db import Base
from pydantic import BaseModel
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class PetDB(Base):
    __tablename__ = "pet"

    user_id: Mapped[str] = mapped_column(String(length=100), index=True, nullable=False)
    chip_id: Mapped[str] = mapped_column(
        String(length=100), primary_key=True, unique=True, index=False, nullable=False
    )
    name: Mapped[str] = mapped_column(String(length=100), index=False, nullable=False)
    is_male: Mapped[bool] = mapped_column(Integer, index=False, nullable=False)
    age: Mapped[int] = mapped_column(Integer, index=False, nullable=False)
    weight: Mapped[float] = mapped_column(Integer, index=False, nullable=False)
    pet_type: Mapped[int] = mapped_column(Integer, index=False, nullable=False)
    feed_kcal: Mapped[float] = mapped_column(Float, index=False, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(
        String(length=500), index=False, nullable=True
    )


class Pet(BaseModel):
    user_id: str
    chip_id: str
    name: str
    is_male: bool
    age: int
    weight: float
    pet_type: int
    feed_kcal: float
    image_url: Optional[str]
