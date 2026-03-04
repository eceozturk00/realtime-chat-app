from __future__ import annotations
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from .connection_manager import ConnectionManager

app = FastAPI(title="Realtime Chat App", version="1.0.0")
manager = ConnectionManager()


app.mount("/web", StaticFiles(directory="web", html=True), name="web")

@app.get("/", response_class=HTMLResponse)
def home():
    # Redirect-ish landing
    return """
    <html>
      <body style="font-family: Arial; max-width: 700px; margin: 40px auto;">
        <h2>Realtime Chat App</h2>
        <p>Open the chat UI:</p>
        <a href="/web/index.html">/web/index.html</a>
      </body>
    </html>
    """

@app.websocket("/ws/{room}/{username}")
async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    await manager.connect(room, websocket, username)

    # Notify join + user list
    await manager.broadcast(room, {
        "type": "system",
        "room": room,
        "time": datetime.utcnow().isoformat() + "Z",
        "message": f"{username} joined the room.",
        "users": manager.users_in_room(room)
    })

    try:
        while True:
            data = await websocket.receive_json()
            text = (data.get("message") or "").strip()
            if not text:
                continue

            await manager.broadcast(room, {
                "type": "chat",
                "room": room,
                "time": datetime.utcnow().isoformat() + "Z",
                "username": username,
                "message": text,
                "users": manager.users_in_room(room)
            })

    except WebSocketDisconnect:
        left = manager.disconnect(room, websocket) or username
        await manager.broadcast(room, {
            "type": "system",
            "room": room,
            "time": datetime.utcnow().isoformat() + "Z",
            "message": f"{left} left the room.",
            "users": manager.users_in_room(room)
        })
