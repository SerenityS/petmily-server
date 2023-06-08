import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import HTMLResponse

from app.db import User
from app.users import current_active_user
from model.command import Command

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
                pass
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
