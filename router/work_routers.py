from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.future import select

from app.db import User, async_session_maker
from app.users import current_active_user
from model.work import Work, WorkDB


def get_work_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="work: Register Work",
    )
    async def register_work(
        user: User = Depends(current_active_user),
        work: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            session.add(WorkDB(user_id=user.id, work=work))
            await session.commit()

        return {"message": f"{user.nick}: Work registered: {work}"}

    @router.get(
        "",
        name="work: Get Work",
    )
    async def get_work(
        user: User = Depends(current_active_user),
    ):
        work_list: list[Work] = []

        async with async_session_maker() as session:
            q = select(WorkDB).where(WorkDB.user_id == str(user.id))
            result = await session.execute(q)
            for row in result.scalars():
                work_list.append(Work(id=row.id, user_id=row.user_id, work=row.work))

        return work_list

    @router.delete(
        "",
        name="work: Delete Work",
    )
    async def delete_work(
        user: User = Depends(current_active_user),
        id: Optional[int] = None,
    ):
        async with async_session_maker() as session:
            q = delete(WorkDB).where(WorkDB.user_id == str(user.id) and WorkDB.id == id)
            await session.execute(q)
            await session.commit()

        return {"message": f"{user.nick}: Work deleted: {id}"}

    return router
