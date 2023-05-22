from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.db import User
from app.users import current_active_user

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

    async def send_command(self, chip_id: int, command: str):
        for connection in self.active_connections:
            if int(connection.path_params["chip_id"]) == chip_id:
                await connection.send_text(command)

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
    async def websocket_endpoint(websocket: WebSocket, chip_id: int):
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_command(chip_id, f"You wrote: {data}")
                await manager.broadcast(f"Device #{chip_id} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Device #{chip_id} left the chat")

    @router.post(
        "/command",
        name="ws: Send Command to Device",
    )
    async def send_cmd(
        user: User = Depends(current_active_user),
        chip_id: Optional[int] = None,
        command: Optional[str] = None,
    ):
        await manager.send_command(chip_id, command)
        return {"message": f"Command sent to {chip_id}"}

    return router
