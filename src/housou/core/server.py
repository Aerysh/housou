import asyncio

import websockets

clients = set()
clients_lock = asyncio.Lock()


async def handler(websocket):
    async with clients_lock:
        clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            async with clients_lock:
                for client in clients.copy():
                    if client != websocket:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            clients.discard(client)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        async with clients_lock:
            clients.discard(websocket)


async def start_server(host, port):
    print(f"Starting server on {host}:{port}")
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # run forever


def run_server(host, port):
    try:
        asyncio.run(start_server(host, port))
    except KeyboardInterrupt:
        print("\nServer stopped.")
