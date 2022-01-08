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
        print(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

statement_collection = []
current_check = None
statement_order = []
manager = ConnectionManager()
scores = {}
random_statement = []


def function_word_smasher():
    result = ""
    for word in statement_collection:
        result += word
    return result

def changeCurrent():
    '''
    Updates global variable current_check
    current_check will become the first set of statements from statement_collection\n
    e.g. current_check = {"User Truth 1":True, "User Truth 2":True, "User False":False, "user": client_id}\n
    Used to prevent players from guessing on their own statements
    '''
    global current_check
    current_check = statement_collection.pop(0)

def _remove_command_char(string):
    '''
    Input:
    - Command String From User Input
    Output:
    - String with command character stripped off
    '''
    stripped_string =  string[1:]
    return stripped_string

async def handle_TL_submission(websocket,new_string,client_id):
    truth_and_lies = await input_parser.changeTL(websocket, new_string, client_id)
    if truth_and_lies:
        statement_collection.append(truth_and_lies)
    print(statement_collection)
    return

async def show_scores():
    clients = list(scores.keys())
    await manager.broadcast("************************************")
    await manager.broadcast("Current Scores:")
    for client in clients:
        await manager.broadcast(f"  {client}: {scores[client]}")

async def handle_next_arrow(websocket):
    if not statement_collection:
        await websocket.send_text("Nothing next")
    else:
        round_manager.reset_input_count()
        changeCurrent()
        global statement_order
        statement_order = list(current_check.keys())
        global random_statement
        random_statement = statement_order[0:3]
        print(random_statement)
        random.shuffle(random_statement)
        print(random_statement)
        await manager.broadcast(f"""
Enter the corresponding number to what you think is the lie.
1. {random_statement[0]}
2. {random_statement[1]}
3. {random_statement[2]}
Use "!" to guess
""")

async def handle_guess(string:str, websocket, client_id):
    if current_check["user"] is client_id:
        return await websocket.send_text("Not for you")

    if round_manager.check_has_finished(client_id):
        round_manager.update_input_count(client_id)
        
        print(round_manager.input_counter)

        if current_check:
            user_input = _remove_command_char(string)
            if user_input.isdigit() and 1 <= int(user_input) <= 3:
                    index_of_guess = int(user_input)-1
                    statement_guessed = random_statement[index_of_guess]
                    if current_check[statement_guessed] is False:
                        await scoreplus(websocket,client_id)
                    else:
                        await scoreminus(websocket,client_id)
            else:  
                await websocket.send_text("That's unfortunate, you missed the 1,2,3 keys")          
    else:
        await websocket.send_text("You have already guessed")     
    if current_check is None:
        await websocket.send_text("No guessing right now")

def clear_statement_collection():
    """
    Clears global statement_collection, effectively sending game back into collecting statements state
    """
    statement_collection.clear()
    

def add_to_score(client_id):
    """
    Adds 20 points to the given player's score
    """
    scores[client_id] += 20
    print(len(round_manager.input_counter))

async def scoreplus(websocket,client_id):
    """
    Notifies client:
    - that their response was correct
    - their updated score
    """
    await websocket.send_text("You guessed right")
    add_to_score(client_id)
    await websocket.send_text(f"Your score: {scores[client_id]}")
                            
                                
def subtract_from_score(client_id):
    """
    Subtracts 20 points from given player's score
    """
    scores[client_id] -= 20

def get_correct_statement():
    """
    Returns correct statement from current TL_Dict in current check
    """
    correct_statement = list(current_check.keys())[2]
    return correct_statement

async def scoreminus(websocket,client_id):
    """
    Notifies client:
    - that their response was incorrect
    - what the correct response was
    - their updated score
    """
    await websocket.send_text("That was incorrect")
    subtract_from_score(client_id)
    await websocket.send_text(f"The correct answer was: {get_correct_statement()}")
    await websocket.send_text(f"Your score: {scores[client_id]}")

async def check_result(string, websocket, client_id):
    try:
        # Clear user statements
        if string[0] == "#":
            clear_statement_collection()
            await manager.broadcast("Cache has been cleared")
            return

        # Sends a help message to the user
        if string[0] == "?":
            return await input_parser.help(websocket)

        # Broadcast a message to all users
        if string[0] == "2":
            stripped_string = _remove_command_char(string)
            return await manager.broadcast(f'{client_id}: {stripped_string}')

        # Sends users 2T&L
        if string[0] == "@":
            stripped_string = _remove_command_char(string)
            await handle_TL_submission(websocket,stripped_string,client_id)

        # Cycles through user statements in guessing round
        if string[0] == ">":
            await handle_next_arrow(websocket)

        # Displays Player Scores
        if string[0] == "$":
            await show_scores()

        # Manages the guesses from users
        if string[0] == "!":
            await handle_guess(string, websocket, client_id)

    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

async def start_round_call(client_id):
    if len(statement_collection) == len(manager.active_connections):
        await manager.broadcast(f"Everyone has sent in their statements {client_id} please press '>'")

async def change_player_or_start_new_round(client_id):   
    if len(round_manager.input_counter) == (len(manager.active_connections) - 1):
        if len(statement_collection) == 0:
            round_manager.reset_input_count()
            await show_scores()
            await manager.broadcast("Please send in your statements prefixed with '@'")
        else:
            await show_scores()
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




    except WebSocketDisconnect:
        
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

import uvicorn

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port = 8001, log_level = "info")
