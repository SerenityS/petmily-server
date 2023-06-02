import json

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends
from model.command import Command
from model.schedule import Schedule, ScheduleDB
from router.ws_router import ConnectionManager
from sqlalchemy import update
from sqlalchemy.future import select


def get_schedule_data_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="schedule: Post Schedule",
    )
    async def post_schedule_data(
        user: User = Depends(current_active_user),
        schedule: Schedule = None,
    ):
        async with async_session_maker() as session:
            q = select(ScheduleDB).where(ScheduleDB.chip_id == schedule.chip_id)
            result = await session.execute(q)

            if result.scalars().first() is None:
                session.add(ScheduleDB(**schedule.dict()))
            else:
                q = (
                    update(ScheduleDB)
                    .where(ScheduleDB.chip_id == schedule.chip_id)
                    .values(schedule.dict())
                )
                await session.execute(q)
            await session.commit()

        await ConnectionManager().send_command(
            Command(chip_id=schedule.chip_id, command="schedule")
        )

        return {"message": "Schedule Registered"}

    @router.get(
        "",
        name="schedule: Get Schedule",
    )
    async def get_schedule_data(
        chip_id: str = None,
    ):
        async with async_session_maker() as session:
            q = select(ScheduleDB).where(ScheduleDB.chip_id == chip_id)
            result = await session.execute(q)
            for row in result.scalars():
                return json.loads(row.schedule_json)
            return None

    return router
