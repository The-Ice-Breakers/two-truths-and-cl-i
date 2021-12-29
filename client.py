import asyncio
from starlette.websockets import WebSocket
from websockets import connect
from aioconsole import ainput

keep_alive = True

name = input("Whats your name?\n")
async def display_message(websocket):
    while keep_alive:
        rec = await websocket.recv()
        print(rec)
        await asyncio.sleep(0)


async def collect_input(websocket:WebSocket):
    global keep_alive
    inp = None
    while not inp == "q":
        inp = await ainput("> ")
        await websocket.send(inp)

    keep_alive = False


async def gather(uri):
    async with connect(uri) as websocket:
        await asyncio.gather(
            display_message(websocket), collect_input(websocket)
        )


asyncio.run(gather(f"ws://localhost:8001/ws/{name}"))