from typing import List
from Game.two_truths_and_lie import Game

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio

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


cache = []
manager = ConnectionManager()
played = []
def function_word_smasher():
    result = ""
    for word in cache:
        result += word
    return result

async def check_result(string, websocket,client_id):

    if string[0] == "$":
        word = string[1:]
        return await websocket.send_text(word)

    # if string[0] == "%":
    #     if string[1:] == truth[0]:
    #         websocket.send_
    
    if client_id in played:
        await websocket.send_text("wait your turn you loser")
    
        
    if client_id not in played:
        played.append(client_id)
        await say_hello(websocket)


    # users_that_have_gone = []
    #say % is used to mark the end of where the client id is in a string:
    #if string before index of '%' is not in userers_that_have_gone:
    #   Do some function
    # Else:
    #    Do nothing because user is in above list

    if string[0] == "*":
        return await say_hello(websocket)

async def say_hello(websocket):
    await websocket.send_text("Hello Word")


@app.get("/test")
async def get():
    return "Yo Dawg"



@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)    
    try:     
        await websocket.send_text("Give me a word")
        while True:
          word = await websocket.receive_text()
          await check_result(word,websocket,client_id)
          

            
            
    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

import uvicorn

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port = 8001, log_level = "info")
