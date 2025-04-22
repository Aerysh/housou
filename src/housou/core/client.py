import asyncio

import websockets


async def receive_messages(websocket):
    try:
        async for message in websocket:
            print(f"\nReceived: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Disconnected from server.")


async def send_messages(websocket):
    loop = asyncio.get_event_loop()
    try:
        while True:
            message = await loop.run_in_executor(None, input, "Enter message: ")
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed:
        print("Server closed connection.")


async def connect_to_server(host, port):
    uri = f"ws://{host}:{port}"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to server.")
            await asyncio.gather(receive_messages(websocket), send_messages(websocket))
    except Exception as e:
        print(f"Connection error: {e}")


def run_client(host, port):
    try:
        asyncio.run(connect_to_server(host, port))
    except KeyboardInterrupt:
        print("\nClient closed.")
