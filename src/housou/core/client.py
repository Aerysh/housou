import asyncio
import curses

import websockets


async def get_username(stdscr):
    curses.curs_set(1)
    stdscr.erase()
    prompt = "Enter username: "
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()
    loop = asyncio.get_running_loop()
    username_bytes = await loop.run_in_executor(None, stdscr.getstr, 0, len(prompt), 20)
    username = username_bytes.decode("utf-8").strip()
    curses.curs_set(0)
    return username


async def receive_messages(websocket, message_win, lock, message_buffer):
    try:
        async for message in websocket:
            message_buffer.append(message)
            async with lock:
                message_win.erase()
                max_y, max_x = message_win.getmaxyx()
                for idx, msg in enumerate(message_buffer[-max_y:]):
                    message_win.addstr(idx, 0, msg[: max_x - 1])
                message_win.refresh()
    except websockets.exceptions.ConnectionClosed:
        async with lock:
            message_win.erase()
            message_win.addstr(0, 0, "Disconnected from server.")
            message_win.refresh()


async def input_loop(websocket, input_win, message_win, lock, message_buffer, username):
    curses.echo()
    loop = asyncio.get_running_loop()
    while True:
        async with lock:
            input_win.erase()
            input_win.addstr(0, 0, "You: ")
            input_win.refresh()
            curses.curs_set(1)
        height, width = input_win.getmaxyx()
        msg_bytes = await loop.run_in_executor(None, input_win.getstr, 0, 5, width - 6)
        msg = msg_bytes.decode("utf-8").strip()
        curses.curs_set(0)
        if msg:
            if msg.lower() == "/quit":
                disconnect_msg = "You have disconnected."
                async with lock:
                    message_buffer.append(disconnect_msg)
                    message_win.erase()
                    max_y, max_x = message_win.getmaxyx()
                    for idx, m in enumerate(message_buffer[-max_y:]):
                        message_win.addstr(idx, 0, m[: max_x - 1])
                    message_win.refresh()
                await websocket.close()
                break
            full_msg = f"{username}: {msg}"
            async with lock:
                message_buffer.append(full_msg)
                message_win.erase()
                max_y, max_x = message_win.getmaxyx()
                for idx, m in enumerate(message_buffer[-max_y:]):
                    message_win.addstr(idx, 0, m[: max_x - 1])
                message_win.refresh()
            try:
                await websocket.send(full_msg)
            except websockets.exceptions.ConnectionClosed:
                break


async def chat_ui(stdscr, host, port):
    curses.curs_set(0)
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    username = await get_username(stdscr)
    message_win = curses.newwin(height - 2, width, 0, 0)
    input_win = curses.newwin(2, width, height - 2, 0)
    lock = asyncio.Lock()
    message_buffer = []
    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri) as websocket:
        async with lock:
            message_win.erase()
            message_win.addstr(0, 0, f"Connected to server as {username}.")
            message_win.refresh()
        recv_task = asyncio.create_task(
            receive_messages(websocket, message_win, lock, message_buffer)
        )
        input_task = asyncio.create_task(
            input_loop(
                websocket, input_win, message_win, lock, message_buffer, username
            )
        )
        await asyncio.gather(recv_task, input_task)


def run_client(host, port):
    asyncio.run(curses.wrapper(chat_ui, host, port))
