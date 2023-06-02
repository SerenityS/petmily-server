from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends
from model.device_data import DeviceData, DeviceDataDB
from sqlalchemy import update
from sqlalchemy.future import select


def get_petmily_deivce_data_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/device_data",
        name="petmily: Post Device Data",
    )
    async def post_device_data(
        device_data: DeviceData = None,
    ):
        async with async_session_maker() as session:
            q = select(DeviceDataDB).where(DeviceDataDB.chip_id == device_data.chip_id)
            result = await session.execute(q)

            if result.scalars().first() is None:
                session.add(DeviceDataDB(**device_data.dict()))
            else:
                q = (
                    update(DeviceDataDB)
                    .where(DeviceDataDB.chip_id == device_data.chip_id)
                    .values(device_data.dict())
                )
                await session.execute(q)
            await session.commit()

        return {"message": "Device Data Registered"}

    @router.get(
        "/device_data",
        name="petmily: Get Device Data",
    )
    async def get_device_data(
        user: User = Depends(current_active_user), chip_id: str = None
    ):
        async with async_session_maker() as session:
            q = select(DeviceDataDB).where(DeviceDataDB.chip_id == chip_id)
            result = await session.execute(q)
            for row in result.scalars():
                return DeviceData(**row.__dict__)
            return None

    return router
