import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    nick: str
    pass


class UserCreate(schemas.BaseUserCreate):
    nick: str
    pass


class UserUpdate(schemas.BaseUserUpdate):
    nick: str
    pass
