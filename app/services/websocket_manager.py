from typing import Dict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    def register(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket

    def remove(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send(self, user_id: str, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)


websocket_manager = WebSocketManager()
