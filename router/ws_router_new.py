import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from model.command import Command


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


def get_ws_router() -> APIRouter:
    router = APIRouter()
    manager = ConnectionManager()

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

    return router
