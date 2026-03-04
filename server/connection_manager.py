from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Set
from fastapi import WebSocket

@dataclass(frozen=True)
class Client:
    username: str
    websocket: WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        # room -> set of websockets
        self.rooms: Dict[str, Dict[WebSocket, str]] = {}

    async def connect(self, room: str, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = {}
        self.rooms[room][websocket] = username

    def disconnect(self, room: str, websocket: WebSocket) -> str | None:
        if room in self.rooms and websocket in self.rooms[room]:
            username = self.rooms[room].pop(websocket, None)
            if not self.rooms[room]:
                self.rooms.pop(room, None)
            return username
        return None

    async def broadcast(self, room: str, message: dict) -> None:
        if room not in self.rooms:
            return
        dead = []
        for ws in list(self.rooms[room].keys()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(room, ws)

    def users_in_room(self, room: str) -> list[str]:
        if room not in self.rooms:
            return []
        return sorted(set(self.rooms[room].values()))
