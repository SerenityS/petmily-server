import os
import uuid

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from model.pet import PetDB
from sqlalchemy import update

UPLOAD_DIR = "static/images"


def get_petmily_image_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/image",
        name="petmily: Upload Pet Image",
    )
    async def upload_pet_image(
        user: User = Depends(current_active_user),
        file: UploadFile = File(...),
        chip_id: str = None,
    ):
        image = await file.read()
        image_prefix = file.filename.split(".")[-1]

        image_url = f"{str(uuid.uuid4())}.{image_prefix}"
        with open(os.path.join(UPLOAD_DIR, image_url), "wb") as fp:
            fp.write(image)

        async with async_session_maker() as session:
            q = (
                update(PetDB)
                .where(PetDB.user_id == str(user.id) and PetDB.chip_id == chip_id)
                .values(image_url=image_url)
            )
            await session.execute(q)
            await session.commit()

        return {"image_url": image_url}

    @router.get(
        "/image",
        name="petmily: Get Pet Image",
    )
    async def get_pet_image(
        file_name: str = None,
    ):
        return FileResponse(os.path.join(UPLOAD_DIR, file_name))

    return router
