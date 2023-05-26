from typing import Optional

from pydantic import BaseModel


class Command(BaseModel):
    chip_id: str
    command: str
    amount: Optional[int]
