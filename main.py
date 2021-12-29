from typing import List
from Game.two_truths_and_lie import Game

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")

game = Game()
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        game.removePlayer(websocket)
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.get("/test")
async def get():
    return "Yo Dawg"


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    await websocket.send_text("What's Yo Name?")
    
    data = await websocket.receive_text()
            
        
    player = game.addPlayer(websocket, data)
    await manager.broadcast(f"{player.name} has joined the game")
    try:
        pass
        
           

    except WebSocketDisconnect:

        manager.disconnect(websocket)

        await manager.broadcast(f"Client #{client_id} left the chat")

import uvicorn

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port = 8001, log_level = "info")

