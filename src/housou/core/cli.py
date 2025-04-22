import asyncio
import websockets
import argparse

# Server
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


# Client
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


def main():
    parser = argparse.ArgumentParser(prog="broadcast-server")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start the broadcast server")
    start_parser.add_argument(
        "--host", default="localhost", help="Host (default: localhost)"
    )
    start_parser.add_argument(
        "--port", type=int, default=8765, help="Port (default: 8765)"
    )

    connect_parser = subparsers.add_parser("connect", help="Connect as a client")
    connect_parser.add_argument(
        "--host", default="localhost", help="Server host (default: localhost)"
    )
    connect_parser.add_argument(
        "--port", type=int, default=8765, help="Server port (default: 8765)"
    )

    args = parser.parse_args()

    if args.command == "start":
        run_server(args.host, args.port)
    elif args.command == "connect":
        run_client(args.host, args.port)
