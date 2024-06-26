from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users
from fastapi import Depends, FastAPI
from router.history_router import get_history_router
from router.petmily_device_data_router import get_petmily_deivce_data_router
from router.petmily_image_router import get_petmily_image_router
from router.petmily_router import get_petmily_router
from router.schedule_router import get_schedule_data_router
from router.ws_router import get_ws_router

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    get_history_router(),
    prefix="/history",
    tags=["history"],
)
app.include_router(
    get_petmily_router(),
    prefix="/petmily",
    tags=["petmily"],
)
app.include_router(
    get_petmily_deivce_data_router(),
    prefix="/petmily",
    tags=["petmily"],
)
app.include_router(
    get_petmily_image_router(),
    prefix="/petmily",
    tags=["petmily"],
)
app.include_router(
    get_schedule_data_router(),
    prefix="/schedule",
    tags=["schedule"],
)
app.include_router(
    get_ws_router(),
    prefix="/ws",
    tags=["WebSocket"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
