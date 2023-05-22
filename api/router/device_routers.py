from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.future import select

from app.db import User, async_session_maker
from app.users import current_active_user
from model.device import Device, DeviceDB


def get_device_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="device: Register Device",
    )
    async def register_device(
        user: User = Depends(current_active_user),
        name: Optional[str] = None,
        chip_id: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            q = select(DeviceDB).where(DeviceDB.user_id == str(user.id))
            result = await session.execute(q)

            for row in result.scalars():
                if chip_id in row.chip_id:
                    return {"message": "Device already registered"}

            session.add(DeviceDB(user_id=user.id, name=name, chip_id=chip_id))
            await session.commit()

        return {"message": "Device registered"}

    @router.get(
        "",
        name="device: Get Device",
    )
    async def get_device(
        user: User = Depends(current_active_user),
    ):
        device_list: list[Device] = []

        async with async_session_maker() as session:
            q = select(DeviceDB).where(DeviceDB.user_id == str(user.id))
            result = await session.execute(q)
            for row in result.scalars():
                device_list.append(
                    Device(user_id=row.user_id, name=row.name, chip_id=row.chip_id)
                )

        return device_list

    @router.delete(
        "",
        name="device: Delete Device",
    )
    async def delete_device(
        user: User = Depends(current_active_user),
        chip_id: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            q = delete(DeviceDB).where(
                DeviceDB.user_id == str(user.id) and DeviceDB.chip_id == chip_id
            )
            await session.execute(q)
            await session.commit()

        return {"message": "Device deleted"}

    return router
