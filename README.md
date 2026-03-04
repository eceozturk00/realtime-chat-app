# Realtime Chat App (FastAPI + WebSocket)

A multi-room realtime chat application built with **FastAPI WebSockets**.

## Features
- WebSocket-based realtime messaging
- Multi-room support (`/ws/{room}/{username}`)
- Broadcast messages to all clients in the same room
- Minimal web UI served by FastAPI

## Tech Stack
Python, FastAPI, WebSockets, Uvicorn

## Run
```bash
pip install -r requirements.txt
uvicorn server.main:app --reload
