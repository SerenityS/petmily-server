from typing import Optional

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends, HTTPException, status
from model.history import History, HistoryDB
from sqlalchemy import delete
from sqlalchemy.future import select


def get_history_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="history: Add History",
    )
    async def register_history(
        user: User = Depends(current_active_user),
        history: History = None,
    ):
        async with async_session_maker() as session:
            session.add(HistoryDB(**history.dict()))
            await session.commit()

        return {"message": "History Registered"}

    @router.get(
        "",
        name="history: Get History List",
    )
    async def get_history(
        user: User = Depends(current_active_user),
    ):
        history_list: list[History] = []

        async with async_session_maker() as session:
            q = select(HistoryDB).where(HistoryDB.user_id == str(user.id))
            result = await session.execute(q)
            for row in result.scalars():
                history_list.append(
                    History(
                        id=row.id,
                        user_id=row.user_id,
                        chip_id=row.chip_id,
                        consume=row.consume,
                        date=row.date,
                    )
                )

        return history_list

    @router.delete(
        "",
        name="history: Delete History",
    )
    async def delete_history(
        user: User = Depends(current_active_user),
        chip_id: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            q = delete(HistoryDB).where(
                HistoryDB.chip_id == chip_id and HistoryDB.user_id == str(user.id)
            )
            await session.execute(q)
            await session.commit()

        return {"message": "History deleted"}

    return router
