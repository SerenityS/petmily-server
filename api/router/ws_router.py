import json

from app.db import User, async_session_maker
from app.users import current_active_user
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import HTMLResponse
from model.command import Command
from model.device_data import DeviceData, DeviceDataDB
from sqlalchemy import update
from sqlalchemy.future import select

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


async def send_device_data(device_data: DeviceData):
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


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_command(self, command: Command):
        for connection in self.active_connections:
            if connection.path_params["chip_id"] == command.chip_id:
                await connection.send_text(json.dumps(command.dict()))
                return True
            return False

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


def get_ws_router() -> APIRouter:
    router = APIRouter()
    manager = ConnectionManager()

    @router.get(
        "",
        name="ws: WebSocket Test Page",
    )
    async def root():
        return HTMLResponse(html)

    @router.websocket(
        "/{chip_id}",
        name="ws: Connect WebSocket",
    )
    async def websocket_endpoint(websocket: WebSocket, chip_id: str):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                json_data = json.loads(data)

                if json_data["cmd"]:
                    await send_device_data(
                        DeviceData(
                            chip_id=json_data["chip_id"],
                            bowl_amount=json_data["bowl_amount"],
                            feed_box_amount=json_data["feed_box_amount"],
                        )
                    )
                    print(
                        f"INFO:\t\tws: {chip_id} sent DeviceData",
                        flush=True,
                    )

        except WebSocketDisconnect:
            manager.disconnect(websocket)
            print(f"ws: {chip_id} disconnected", flush=True)

    @router.post(
        "/command",
        name="ws: Send Command to Device",
    )
    async def send_cmd(
        user: User = Depends(current_active_user), command: Command = None
    ):
        result = await manager.send_command(command)
        if result:
            return {"message": f"Command sent to {command.chip_id}"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )

    return router
