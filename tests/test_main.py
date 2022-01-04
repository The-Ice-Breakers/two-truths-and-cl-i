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

    def connect(self, websocket: WebSocket):
        websocket.accept()
        self.active_connections.append(websocket)
        print(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            connection.send_text(message)


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


def check_result(string, websocket,client_id):
    try:
        if string[0] == "#":
            cache.clear()
            manager.broadcast("Cache has been cleared")
            return

        if string[0] == "?":
            new_string = string[1:]
            return input_parser.help(websocket)

        if string[0] == "2":
            new_string = string[1:]
            return manager.broadcast(new_string)

        if string[0] == "@":
            new_string = string[1:]
            truth_and_lies = input_parser.changeTL(websocket, new_string, client_id)
            if truth_and_lies:
                cache.append(truth_and_lies)
            print(cache)
            return truth_and_lies

        if string[0] == ">":
            if not cache:
                return websocket.send_text("Nothing next")
            else:
                round_manager.reset_input_count()
                changeCurrent()
                global statement_order
                statement_order = list(current_check.keys())
                global random_statement
                random_statement = statement_order[0:3]
                random.shuffle(random_statement)
                manager.broadcast(f"""
    Enter the corresponding number to what you think is the lie.
    1. {random_statement[0]}
    2. {random_statement[1]}
    3. {random_statement[2]}
    Use "!" to guess
    """)

        if string[0] == "!":
            if current_check["user"] is client_id:
                return websocket.send_text("Not for you")

            if round_manager.check_has_finished(client_id):

                round_manager.update_input_count(client_id)
                print(round_manager.input_counter)
                if current_check:
                    new_string = string[1:]
                    if new_string.isdigit() and 0 < int(new_string) < 4:
            
                            if current_check[random_statement[int(new_string)-1]] is False:
                                websocket.send_text("You guessed right")
                                scores[client_id] += 20
                                print(len(round_manager.input_counter))
                                websocket.send_text(f"Your score: {scores[client_id]}")
                            else: 
                                websocket.send_text("That was incorrect")
                                scores[client_id] -= 20
                                correct_list = list(current_check.keys())
                                websocket.send_text(f"The correct answer was: {correct_list[2]}")
                                websocket.send_text(f"Your score: {scores[client_id]}")
    
                    else:  
                        websocket.send_text("That's unfortunate, you missed the 1,2,3 keys")          
            else:
                websocket.send_text("You have already guessed")     
            if current_check is None:
                websocket.send_text("No guessing right now")

    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        manager.broadcast(f"Client #{client_id} left the chat")

def start_round_call(client_id):
    if len(cache) == len(manager.active_connections):
        manager.broadcast(f"Everyone has sent in their statments {client_id} please press '>'")

def change_player_or_start_new_round(client_id):   
    if len(round_manager.input_counter) == (len(manager.active_connections) - 1):
        if len(cache) == 0:
            round_manager.reset_input_count()
            manager.broadcast("Please send in your statements prefixed with '@'")
        else:
            manager.broadcast(f"Everyone has guessed {client_id} please press '>' ")


@app.get("/test")
def get():
    return "Yo Dawg"


@app.websocket("/ws/{client_id}")
def websocket_endpoint(websocket: WebSocket, client_id: str):
    manager.connect(websocket)    
    scores[client_id] = 0
    try:     
        websocket.send_text("""For help with commands enter "?" """)
        websocket.send_text("Please send in your statements prefixed with '@'")
        while True:
            word = websocket.receive_text()
            check_result(word,websocket,client_id)
            start_round_call(client_id)
            change_player_or_start_new_round(client_id)
            print("cool")



    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        manager.broadcast(f"Client #{client_id} left the chat")

import uvicorn

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port = 8001, log_level = "info")
