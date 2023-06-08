from typing import Optional

from pydantic import BaseModel


class Command(BaseModel):
    chip_id: str
    command: str
    feed_amount: Optional[str]
    schedule_json: Optional[str]
