from typing import Counter, List
from Game.server_functions import Parser, RoundManager
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import re
app = FastAPI()
input_parser = Parser()
round_manager = RoundManager(1)
# app.mount("/static", StaticFiles(directory="static"), name="static")



class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


cache = []
current_check = None
statement_order = []
manager = ConnectionManager()
scores = {}
random_statement = []

def function_word_smasher():
    result = ""
    for word in cache:
        result += word
    return result

def changeCurrent():
    global current_check
    current_check = cache.pop(0)


async def check_result(string, websocket,client_id):
    try:

        if string[0] == "?":
            new_string = string[1:]
            return await input_parser.help(websocket)

        if string[0] == "2":
            new_string = string[1:]
            return await manager.broadcast(new_string)

        if string[0] == "@":
            new_string = string[1:]
            truth_and_lies = await input_parser.changeTL(websocket, new_string, client_id)
            if truth_and_lies:
                cache.append(truth_and_lies)
            print(cache)
            return

        if string[0] == ">":
            if not cache:
                await websocket.send_text("Nothing next")
            else:
                round_manager.reset_input_count()
                changeCurrent()
                global statement_order
                statement_order = list(current_check.keys())
                global random_statement
                random_statement = statement_order[0:3]
                random.shuffle(random_statement)
                await manager.broadcast(f"""
    Enter the corresponding number to what you think is the lie.
    1. {random_statement[0]}
    2. {random_statement[1]}
    3. {random_statement[2]}
    Use "!" to guess
    """)

        if string[0] == "!":
            if current_check["user"] is client_id:
                return await websocket.send_text("Not for you")

            if round_manager.check_has_finished(client_id):

                round_manager.update_input_count(client_id)
                print(round_manager.input_counter)
                if current_check:
                    new_string = string[1:]
                    if new_string.isdigit() and 0 < int(new_string) < 4:
            
                            if current_check[random_statement[int(new_string)-1]] is False:
                                await websocket.send_text("You guessed right")
                                scores[client_id] += 20
                                print(len(round_manager.input_counter))
                                await websocket.send_text(f"Your score: {scores[client_id]}")
                            else: 
                                await websocket.send_text("That was incorrect")
                                scores[client_id] -= 20
                                correct_list = list(current_check.keys())
                                await websocket.send_text(f"The correct answer was: {correct_list[2]}")
                                await websocket.send_text(f"Your score: {scores[client_id]}")
    
                    else:  
                        await websocket.send_text("That's unfortunate, you missed the 1,2,3 keys")          
            else:
                await websocket.send_text("You have already guessed")     
            if current_check is None:
                await websocket.send_text("No guessing right now")

    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

async def start_round_call(client_id):
    if len(cache) == len(manager.active_connections):
        await manager.broadcast(f"Everyone has sent in their statments {client_id} please press '>'")

async def change_player_or_start_new_round(client_id):   
    if len(round_manager.input_counter) == (len(manager.active_connections) - 1):
        if len(cache) == 0:
            round_manager.reset_input_count()
            await manager.broadcast("Please send in your statements prefixed with '@'")
        else:
            await manager.broadcast(f"Everyone has guessed {client_id} please press '>' ")


@app.get("/test")
async def get():
    return "Yo Dawg"


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)    
    scores[client_id] = 0
    try:     
        await websocket.send_text("""For help with commands enter "?" """)
        await websocket.send_text("Please send in your statements prefixed with '@'")
        while True:
            word = await websocket.receive_text()
            await check_result(word,websocket,client_id)
            await start_round_call(client_id)
            await change_player_or_start_new_round(client_id)
            print("cool")



    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

import uvicorn

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port = 8001, log_level = "info")
