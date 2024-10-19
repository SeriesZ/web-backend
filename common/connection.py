from collections import defaultdict
from typing import List, Dict

from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    # async def send_message(self, message: str, websocket: WebSocket):
    #     await websocket.send_text(message)
    #
    # async def broadcast(self, room_id: str, message: str):
    #     for connection in self.active_connections[room_id]:
    #         await connection.send_text(message)


manager_instance = ConnectionManager()


def get_manager():
    return manager_instance
