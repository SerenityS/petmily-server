import os
import uuid
from typing import Optional

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from model.pet import Pet, PetDB
from sqlalchemy import delete, update
from sqlalchemy.future import select

UPLOAD_DIR = "static/images"


def get_pet_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "",
        name="pet: Register Pet",
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

    @router.post(
        "/image",
        name="pet: Upload Pet Image",
    )
    async def upload_pet_image(
        user: User = Depends(current_active_user),
        file: UploadFile = File(...),
        pet: Pet = None,
    ):
        image = await file.read()
        image_prefix = file.filename.split(".")[-1]

        image_url = f"{str(uuid.uuid4())}.{image_prefix}"
        with open(os.path.join(UPLOAD_DIR, image_url), "wb") as fp:
            fp.write(image)

        async with async_session_maker() as session:
            q = (
                update(PetDB)
                .where(PetDB.user_id == str(user.id) and PetDB.chip_id == pet.chip_id)
                .values(image_url=image_url)
            )
            await session.execute(q)
            await session.commit()

        return {"image_url": image_url}

    @router.get(
        "",
        name="pet: Get Pet List",
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

    @router.get(
        "/image",
        name="pet: Get Pet Image",
    )
    async def get_pet_image(
        user: User = Depends(current_active_user),
        file_name: str = None,
    ):
        return FileResponse(os.path.join(UPLOAD_DIR, file_name))

    @router.patch(
        "",
        name="pet: Update Pet",
    )
    async def update_pet(
        user: User = Depends(current_active_user),
        pet: Pet = None,
    ):
        async with async_session_maker() as session:
            q = (
                update(PetDB)
                .where(PetDB.user_id == str(user.id) and PetDB.chip_id == pet.chip_id)
                .values(pet.dict())
            )
            await session.execute(q)
            await session.commit()

        return {"message": "Pet Updated"}

    @router.delete(
        "",
        name="pet: Delete Pet",
    )
    async def delete_pet(
        user: User = Depends(current_active_user),
        chip_id: Optional[str] = None,
    ):
        async with async_session_maker() as session:
            q = delete(PetDB).where(
                PetDB.user_id == str(user.id) and PetDB.chip_id == chip_id
            )
            await session.execute(q)
            await session.commit()

        return {"message": "Pet deleted"}

    return router
