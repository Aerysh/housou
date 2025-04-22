import argparse

from housou.core.client import run_client
from housou.core.server import run_server


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
