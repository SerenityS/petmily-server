from typing import Optional

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends, HTTPException, status
from model.pet import Pet, PetDB
from sqlalchemy import delete, update
from sqlalchemy.future import select


def get_petmily_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="petmily: Register Pet",
    )
    async def register_pet(
        user: User = Depends(current_active_user),
        pet: Pet = None,
    ):
        async with async_session_maker() as session:
            q = select(PetDB).where(PetDB.chip_id == str(pet.chip_id))
            result = await session.execute(q)

            for row in result.scalars():
                if pet.chip_id in row.chip_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pet already registered",
                    )

            session.add(PetDB(**pet.dict()))
            await session.commit()

        return {"message": "Pet Registered"}

    @router.get(
        "",
        name="petmily: Get Pet List",
    )
    async def get_pet(
        user: User = Depends(current_active_user),
    ):
        pet_list: list[Pet] = []

        async with async_session_maker() as session:
            q = select(PetDB).where(PetDB.user_id == str(user.id))
            result = await session.execute(q)
            for row in result.scalars():
                pet_list.append(
                    Pet(
                        user_id=row.user_id,
                        chip_id=row.chip_id,
                        name=row.name,
                        is_male=row.is_male,
                        age=row.age,
                        weight=row.weight,
                        pet_type=row.pet_type,
                        feed_kcal=row.feed_kcal,
                        image_url=row.image_url,
                    )
                )

        return pet_list

    @router.patch(
        "",
        name="petmily: Update Pet",
    )
    async def update_pet(
        user: User = Depends(current_active_user),
        pet: Pet = None,
    ):
        async with async_session_maker() as session:
            q = (
                update(PetDB)
                .where(PetDB.chip_id == pet.chip_id and PetDB.user_id == str(user.id))
                .values(pet.dict())
            )
            await session.execute(q)
            await session.commit()

        return {"message": "Pet Updated"}

    @router.delete(
        "",
        name="petmily: Delete Pet",
    )
    async def delete_pet(
        user: User = Depends(current_active_user),
        chip_id: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            q = delete(PetDB).where(
                PetDB.chip_id == chip_id and PetDB.user_id == str(user.id)
            )
            await session.execute(q)
            await session.commit()

        return {"message": "Pet deleted"}

    return router
